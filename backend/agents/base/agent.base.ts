import { MCPMessageBus } from '../../mcp-bus/src/bus/message-bus';
import { ContextManager } from '../../mcp-bus/src/context/context-manager';
import {
  MCPMessage,
  AgentType,
  MessageType,
  MessagePriority,
  AgentCapability
} from '../../mcp-bus/src/protocols/mcp.protocol';

export abstract class BaseAgent {
  protected agentType: AgentType;
  protected messageBus: MCPMessageBus;
  protected contextManager: ContextManager;
  protected capabilities: AgentCapability;

  constructor(
    agentType: AgentType,
    messageBus: MCPMessageBus,
    contextManager: ContextManager
  ) {
    this.agentType = agentType;
    this.messageBus = messageBus;
    this.contextManager = contextManager;
    this.capabilities = this.defineCapabilities();
  }

  /**
   * Each agent must define its capabilities
   */
  protected abstract defineCapabilities(): AgentCapability;

  /**
   * Main message handler - to be implemented by each agent
   */
  protected abstract handleMessage(message: MCPMessage): Promise<any>;

  /**
   * Start the agent
   */
  async start() {
    console.log(`🚀 Starting ${this.agentType} agent...`);

    // Subscribe to messages
    await this.messageBus.subscribe(this.agentType, async (message) => {
      try {
        console.log(`📨 ${this.agentType} received message:`, message.type);
        const result = await this.handleMessage(message);

        // Send response if it was a request
        if (message.type === MessageType.REQUEST) {
          await this.sendResponse(message, result);
        }
      } catch (error: any) {
        console.error(`❌ ${this.agentType} error:`, error);
        if (message.type === MessageType.REQUEST) {
          await this.sendError(message, error);
        }
      }
    });

    console.log(`✅ ${this.agentType} agent ready`);
  }

  /**
   * Send message to another agent
   */
  protected async sendMessage(
    target: AgentType | AgentType[],
    type: MessageType,
    payload: any,
    context?: any,
    priority: MessagePriority = MessagePriority.NORMAL
  ): Promise<string> {
    return this.messageBus.publish({
      type,
      source: this.agentType,
      target,
      payload,
      context,
      priority
    });
  }

  /**
   * Request-Reply to another agent
   */
  protected async requestFromAgent(
    target: AgentType,
    payload: any,
    context?: any
  ): Promise<any> {
    return this.messageBus.request(target, payload, context);
  }

  /**
   * Broadcast event to all agents
   */
  protected async broadcast(payload: any, context?: any): Promise<string> {
    return this.messageBus.publish({
      type: MessageType.BROADCAST,
      source: this.agentType,
      payload,
      context,
      priority: MessagePriority.NORMAL
    });
  }

  /**
   * Send response to a request
   */
  private async sendResponse(originalMessage: MCPMessage, result: any) {
    await this.sendMessage(
      originalMessage.source,
      MessageType.RESPONSE,
      {
        success: true,
        data: result,
        requestId: originalMessage.id
      },
      originalMessage.context,
      MessagePriority.HIGH
    );
  }

  /**
   * Send error response
   */
  private async sendError(originalMessage: MCPMessage, error: any) {
    await this.sendMessage(
      originalMessage.source,
      MessageType.RESPONSE,
      {
        success: false,
        error: error.message,
        requestId: originalMessage.id
      },
      originalMessage.context,
      MessagePriority.HIGH
    );
  }

  /**
   * Get context for current operation
   */
  protected async getContext(farmerId?: string, fpoId?: string): Promise<any> {
    if (farmerId) {
      return this.contextManager.getFarmerContext(farmerId);
    }
    if (fpoId) {
      return this.contextManager.getFPOContext(fpoId);
    }
    return {};
  }

  /**
   * Update context
   */
  protected async updateContext(
    farmerId: string,
    contextType: string,
    data: any
  ): Promise<void> {
    await this.contextManager.updateContext(farmerId, contextType as any, data);
  }

  /**
   * Log agent activity
   */
  protected log(message: string, data?: any) {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [${this.agentType}] ${message}`, data || '');
  }

  /**
   * Get agent capabilities
   */
  getCapabilities(): AgentCapability {
    return this.capabilities;
  }
}
