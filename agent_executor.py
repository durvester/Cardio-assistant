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
    Task, TaskStatus, TaskState, Message, TextPart, Part, TaskArtifactUpdateEvent
)
from a2a.utils import (
    new_agent_text_message,
    new_task,
    new_text_artifact,
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
        
    async def execute_streaming(
        self,
        context: RequestContext,
        event_queue: EventQueue
    ) -> None:
        """
        Streaming implementation following LangGraph pattern.
        Consumes agent's stream_process and translates to A2A events.
        """
        try:
            message_text = self._extract_message_text(context.message)
            
            if not message_text:
                await self._handle_error(
                    event_queue, 
                    context.task_id, 
                    context.context_id,
                    "No message text found in request"
                )
                return
            
            logger.info(f"Executing streaming task {context.task_id}")
            
            # Get or create task (following LangGraph pattern)
            task = context.current_task
            if not task:
                task = new_task(context.message)
                await event_queue.enqueue_event(task)
            
            # Create TaskUpdater for A2A event management
            updater = TaskUpdater(event_queue, task.id, task.context_id)
            
            # Get conversation history
            conversation_history = task.history if task.history else []
            
            logger.info(f"Streaming with {len(conversation_history)} messages in history")
            
            # Stream through the agent process
            async for item in cardiology_agent.stream_process(message_text, conversation_history):
                is_task_complete = item['is_task_complete']
                require_user_input = item['require_user_input']
                content = item['content']
                
                if not is_task_complete and not require_user_input:
                    # Intermediate update - use TaskState.working with final=False
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(content, task.context_id, task.id),
                        final=False  # This enables streaming
                    )
                elif require_user_input:
                    # Needs user input - use TaskState.input_required with final=True
                    await updater.update_status(
                        TaskState.input_required,
                        new_agent_text_message(content, task.context_id, task.id),
                        final=True  # End this streaming cycle
                    )
                    break
                else:
                    # Task complete - send final status with the result content
                    # Per A2A spec: final=True signals end of updates when task reaches terminal state
                    await updater.update_status(
                        TaskState.completed,
                        new_agent_text_message(content, task.context_id, task.id),
                        final=True  # End this streaming cycle - task reached terminal state
                    )
                    
                    # Note: TaskArtifactUpdateEvent would be used here if we had large files
                    # or structured data that needed to be delivered as artifacts.
                    # For simple text responses, the status message is sufficient.
                    # 
                    # Example artifact delivery (commented out):
                    # if self._should_send_as_artifact(content):
                    #     await self._send_artifact(event_queue, task, content)
                    break
            
            logger.info(f"Streaming task {context.task_id} completed")
                    
        except Exception as e:
            logger.error(f"Error executing streaming task {context.task_id}: {e}")
            await self._handle_error(
                event_queue, 
                context.task_id, 
                context.context_id,
                f"Streaming error: {str(e)}"
            )

    async def execute(
        self, 
        context: RequestContext, 
        event_queue: EventQueue
    ) -> None:
        """
        Execute the agent's logic using streaming implementation.
        This method now delegates to the streaming implementation.
        """
        # Simply delegate to the streaming implementation
        await self.execute_streaming(context, event_queue)
    
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
            
            # Create basic failed task for error cases
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
    
    def _should_send_as_artifact(self, content: str) -> bool:
        """
        Determine if content should be sent as an artifact rather than a status message.
        
        Per A2A spec, TaskArtifactUpdateEvent is for:
        - Large files or data structures  
        - Content that needs to be streamed in chunks
        - Structured data that clients need to process separately
        
        Args:
            content: The response content to evaluate
            
        Returns:
            bool: True if content should be sent as artifact
        """
        # Example criteria for when to use artifacts:
        # - Large content (>1KB)
        # - JSON/XML structured data
        # - File attachments
        # - Multi-part responses
        
        if len(content) > 1024:  # Large content
            return True
            
        if content.strip().startswith('{') or content.strip().startswith('['):  # JSON
            return True
            
        if content.strip().startswith('<'):  # XML
            return True
            
        return False
    
    async def _send_artifact(self, event_queue: EventQueue, task: Task, content: str) -> None:
        """
        Send content as a TaskArtifactUpdateEvent.
        
        Args:
            event_queue: Event queue for publishing
            task: Current task context
            content: Content to send as artifact
        """
        artifact = new_text_artifact(
            name="referral_result",
            text=content,
            description="Detailed referral processing result"
        )
        
        artifact_event = TaskArtifactUpdateEvent(
            taskId=task.id,
            contextId=task.context_id,
            artifact=artifact,
            lastChunk=True  # Complete artifact (not streamed in chunks)
        )
        
        await event_queue.enqueue_event(artifact_event)
        logger.info(f"Sent artifact for task {task.id}")


# Global executor instance
cardiology_executor = CardiologyAgentExecutor()
