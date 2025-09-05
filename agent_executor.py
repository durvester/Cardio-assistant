"""
A2A Protocol Bridge for the Walter Reed Cardiology Agent.

This module implements the AgentExecutor interface, bridging between the A2A protocol
and the core agent business logic.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional

from a2a.server.agent_execution.agent_executor import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    Task, TaskStatus, TaskState, Message, TextPart
)
from a2a.utils import (
    new_agent_text_message,
    new_task,
)

from agent import cardiology_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class CardiologyAgentExecutor(AgentExecutor):
    """
    A2A AgentExecutor implementation for the Cardiology Referral Agent.
    
    This class handles the A2A protocol interactions and delegates the actual
    message processing to the CardiologyAgent business logic.
    """
    
    def __init__(self):
        """Initialize the executor."""
        logger.info("Initializing CardiologyAgentExecutor")
        
    async def execute(
        self, 
        context: RequestContext, 
        event_queue: EventQueue
    ) -> None:
        """
        Execute the agent's logic for processing a cardiology referral request.
        
        Supports both Phase 1 (single-turn) and Phase 2 (multi-turn) conversations.
        The LLM determines state transitions through special markers in responses.
        
        Args:
            context: The request context containing the message and task information
            event_queue: The queue to publish events to
        """
        try:
            logger.info(f"Executing task {context.task_id}")
            
            # Extract message text from the request
            message_text = self._extract_message_text(context.message)
            
            if not message_text:
                await self._handle_error(
                    event_queue, 
                    context.task_id, 
                    context.context_id,
                    "No message text found in request"
                )
                return
            
            logger.info(f"Processing message: {message_text[:100]}...")
            
            # Follow LangGraph pattern exactly: get or create task
            task = context.current_task
            if not task:
                task = new_task(context.message)
                await event_queue.enqueue_event(task)
            
            # Create TaskUpdater for proper SDK communication
            updater = TaskUpdater(event_queue, task.id, task.context_id)
            
            # Get conversation history from existing task
            conversation_history = task.history if task.history else []
            
            # Log for monitoring
            if context.current_task:
                logger.info(f"Continuing existing task with {len(conversation_history)} messages in history")
            else:
                logger.info("Created new task")
                
            logger.info(f"Task mode: {'Multi-turn continuation' if context.current_task else 'New task'}")
            logger.info(f"Conversation history length: {len(conversation_history)}")
            
            # Process message with appropriate context
            # For Phase 2, we want to use multi-turn mode in most cases to enable LLM
            # to decide if it needs more information. Use Phase 1 mode only for 
            # very clearly complete requests.
            
            # Improved heuristic for Phase 1 detection:
            # Must have multiple required elements AND be long enough
            has_patient_info = any(keyword in message_text.lower() for keyword in [
                "patient", "name", "dob", "birth", "mrn"
            ])
            has_provider_info = any(keyword in message_text.lower() for keyword in [
                "dr.", "doctor", "physician", "npi", "referring"
            ])
            has_clinical_info = any(keyword in message_text.lower() for keyword in [
                "chest pain", "arrhythmia", "symptoms", "condition", "ekg", "ecg"
            ])
            has_insurance_info = any(keyword in message_text.lower() for keyword in [
                "insurance", "aetna", "blue cross", "united", "cigna", "member id"
            ])
            
            # Only use Phase 1 if this looks like a complete referral with most elements
            complete_elements = sum([has_patient_info, has_provider_info, has_clinical_info, has_insurance_info])
            is_likely_complete_referral = (complete_elements >= 3 and len(message_text.split()) > 20)
            
            if conversation_history or context.current_task or not is_likely_complete_referral:
                # Phase 2: Multi-turn conversation (new or continuing)
                # Pass empty list for new tasks to trigger multi-turn system prompt
                history_to_pass = conversation_history if conversation_history else []
                response_text = await cardiology_agent.process_message(message_text, history_to_pass)
            else:
                # Phase 1: Single-turn conversation (backward compatibility for very complete requests)
                logger.info("Using Phase 1 mode for complete referral request")
                response_text = await cardiology_agent.process_message(message_text)
            
            # Extract LLM's state decision from response markers
            task_state, clean_response_text = self._extract_llm_state_decision(response_text)
            
            logger.info(f"LLM decided task state: {task_state}")
            
            # Create agent message using SDK utility
            agent_message = new_agent_text_message(
                clean_response_text,
                task.context_id,
                task.id
            )
            
            # Use TaskUpdater to properly update task status
            if task_state == TaskState.input_required:
                await updater.update_status(
                    TaskState.input_required,
                    agent_message,
                    final=True
                )
            elif task_state == TaskState.completed:
                await updater.update_status(
                    TaskState.completed,
                    agent_message,
                    final=True
                )
            elif task_state == TaskState.failed:
                await updater.update_status(
                    TaskState.failed,
                    agent_message,
                    final=True
                )
            else:
                # Default to working state
                await updater.update_status(
                    TaskState.working,
                    agent_message
                )
            
            logger.info(f"Task {context.task_id} updated with state: {task_state}")
            
        except Exception as e:
            logger.error(f"Error executing task {context.task_id}: {e}")
            await self._handle_error(
                event_queue, 
                context.task_id, 
                context.context_id,
                f"Internal error: {str(e)}"
            )
    
    async def cancel(
        self, 
        context: RequestContext, 
        event_queue: EventQueue
    ) -> None:
        """
        Cancel an ongoing task.
        
        Args:
            context: The request context containing the task ID to cancel
            event_queue: The queue to publish the cancellation status to
        """
        try:
            logger.info(f"Canceling task {context.task_id}")
            
            # Use TaskUpdater pattern for cancellation
            task = context.current_task
            if task:
                updater = TaskUpdater(event_queue, task.id, task.context_id)
                await updater.update_status(
                    TaskState.canceled,
                    final=True
                )
            else:
                # Fallback: create basic canceled task
                canceled_task = Task(
                    id=context.task_id,
                    context_id=context.context_id,
                    status=TaskStatus(
                        state=TaskState.canceled,
                        timestamp=datetime.utcnow().isoformat() + "Z"
                    ),
                    history=[],
                    artifacts=[],
                    kind="task"
                )
                await event_queue.enqueue_event(canceled_task)
            logger.info(f"Task {context.task_id} canceled")
            
        except Exception as e:
            logger.error(f"Error canceling task {context.task_id}: {e}")
            # Still try to mark as failed
            await self._handle_error(
                event_queue, 
                context.task_id, 
                context.context_id,
                f"Error during cancellation: {str(e)}"
            )
    
    def _extract_message_text(self, message: Message) -> Optional[str]:
        """
        Extract text content from a message.
        
        Args:
            message: The A2A message object
            
        Returns:
            The text content or None if no text found
        """
        try:
            logger.info(f"Extracting text from message with {len(message.parts)} parts")
            
            for part in message.parts:
                # Part is a RootModel union type, access the actual part via .root
                if hasattr(part, 'root'):
                    actual_part = part.root
                    
                    # Check if this is a TextPart with kind="text"
                    if hasattr(actual_part, 'kind') and actual_part.kind == "text" and hasattr(actual_part, 'text'):
                        logger.info(f"Found text part: {actual_part.text[:100]}...")
                        return actual_part.text
                        
            logger.warning("No text parts found in message")
            return None
        except Exception as e:
            logger.error(f"Error extracting message text: {e}")
            return None

    def _extract_llm_state_decision(self, llm_response: str) -> tuple[TaskState, str]:
        """
        Extract the task state decision from LLM response markers.
        
        Args:
            llm_response: The LLM's response text with potential state markers
            
        Returns:
            Tuple of (TaskState, clean_response_text)
        """
        # Check for LLM state control markers
        if "[NEED_MORE_INFO]" in llm_response:
            clean_response = llm_response.replace("[NEED_MORE_INFO]", "").strip()
            logger.info("LLM requested more information - transitioning to input-required")
            return TaskState.input_required, clean_response
            
        elif "[REFERRAL_COMPLETE]" in llm_response:
            clean_response = llm_response.replace("[REFERRAL_COMPLETE]", "").strip()
            logger.info("LLM completed referral - transitioning to completed")
            return TaskState.completed, clean_response
            
        elif "[REFERRAL_FAILED]" in llm_response:
            clean_response = llm_response.replace("[REFERRAL_FAILED]", "").strip()
            logger.info("LLM failed referral - transitioning to failed")
            return TaskState.failed, clean_response
        
        else:
            # Default behavior for backward compatibility (Phase 1)
            # If no markers, assume completed (Phase 1 behavior)
            logger.info("No state markers found - defaulting to completed (Phase 1 compatibility)")
            return TaskState.completed, llm_response

    def _create_task_status(self, task_state: TaskState, agent_message: Message) -> TaskStatus:
        """
        Create appropriate TaskStatus based on the LLM's state decision.
        
        Args:
            task_state: The state determined by the LLM
            agent_message: The agent's response message
            
        Returns:
            TaskStatus object
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        if task_state == TaskState.input_required:
            # For input-required, include the agent's question as the status message
            return TaskStatus(
                state=TaskState.input_required,
                message=agent_message,  # Agent's question becomes the status message
                timestamp=timestamp
            )
        elif task_state == TaskState.failed:
            # For failed tasks, include the error message
            return TaskStatus(
                state=TaskState.failed,
                message=agent_message,  # Agent's error explanation
                timestamp=timestamp
            )
        else:
            # For completed tasks, just state and timestamp
            return TaskStatus(
                state=task_state,
                timestamp=timestamp
            )
    
    
    async def _handle_error(
        self, 
        event_queue: EventQueue, 
        task_id: str, 
        context_id: str,
        error_message: str
    ) -> None:
        """
        Handle an error by creating a failed task with error response.
        
        Args:
            event_queue: The event queue to publish to
            task_id: The task ID
            context_id: The context ID
            error_message: The error message to send
        """
        try:
            # Create error response message
            error_response = Message(
                role="agent",
                parts=[TextPart(
                    kind="text", 
                    text=f"I apologize, but I encountered an error processing your request: {error_message}. Please try again or contact Dr. Walter Reed's office directly."
                )],
                message_id=str(uuid.uuid4()),
                task_id=task_id,
                context_id=context_id,
                kind="message"
            )
            
            # Use TaskUpdater pattern for error handling
            # First ensure we have a task
            task = context.current_task
            if not task:
                task = new_task(context.message) if context.message else None
                if task:
                    await event_queue.enqueue_event(task)
            
            if task:
                updater = TaskUpdater(event_queue, task.id, task.context_id)
                await updater.update_status(
                    TaskState.failed,
                    error_response,
                    final=True
                )
            else:
                # Fallback: create basic failed task
                failed_task = Task(
                    id=task_id,
                    context_id=context_id,
                    status=TaskStatus(
                        state=TaskState.failed,
                        message=error_response,
                        timestamp=datetime.utcnow().isoformat() + "Z"
                    ),
                    history=[error_response],
                    artifacts=[],
                    kind="task"
                )
                await event_queue.enqueue_event(failed_task)
            
        except Exception as e:
            logger.error(f"Error in error handler: {e}")


# Global executor instance
cardiology_executor = CardiologyAgentExecutor()
