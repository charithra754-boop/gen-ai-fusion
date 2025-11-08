import Redis from 'ioredis';
import { ContextState, FarmContext, MarketContext, FPOContext } from '../protocols/mcp.protocol';

export class ContextManager {
  private redis: Redis;
  private readonly TTL = 3600; // 1 hour

  constructor(redisUrl: string) {
    this.redis = new Redis(redisUrl);
  }

  /**
   * Get complete context for a farmer
   */
  async getFarmerContext(farmerId: string): Promise<ContextState> {
    const key = `context:farmer:${farmerId}`;
    const data = await this.redis.get(key);
    return data ? JSON.parse(data) : {};
  }

  /**
   * Update specific context slice
   */
  async updateContext(
    farmerId: string,
    contextType: keyof ContextState,
    data: any
  ): Promise<void> {
    const key = `context:farmer:${farmerId}`;
    const existing = await this.getFarmerContext(farmerId);

    existing[contextType] = {
      ...existing[contextType],
      ...data,
      updatedAt: new Date()
    };

    await this.redis.setex(key, this.TTL, JSON.stringify(existing));
  }

  /**
   * Get FPO-level context
   */
  async getFPOContext(fpoId: string): Promise<any> {
    const key = `context:fpo:${fpoId}`;
    const data = await this.redis.get(key);
    return data ? JSON.parse(data) : {};
  }

  /**
   * Update FPO context
   */
  async updateFPOContext(fpoId: string, data: any): Promise<void> {
    const key = `context:fpo:${fpoId}`;
    const existing = await this.getFPOContext(fpoId);

    const updated = {
      ...existing,
      ...data,
      updatedAt: new Date()
    };

    await this.redis.setex(key, this.TTL * 24, JSON.stringify(updated)); // 24 hour TTL for FPO
  }

  /**
   * Resolve context from message chain
   */
  async resolveMessageContext(messageIds: string[]): Promise<ContextState> {
    const contexts = await Promise.all(
      messageIds.map(id => this.redis.get(`mcp:message:${id}`))
    );

    // Merge contexts in chronological order
    return contexts.reduce((merged, ctx) => {
      if (ctx) {
        const parsed = JSON.parse(ctx);
        return { ...merged, ...parsed.context };
      }
      return merged;
    }, {});
  }

  /**
   * Clear context for a farmer (e.g., on logout)
   */
  async clearFarmerContext(farmerId: string): Promise<void> {
    const key = `context:farmer:${farmerId}`;
    await this.redis.del(key);
  }

  /**
   * Get all active farmer contexts (for monitoring/debugging)
   */
  async getActiveFarmers(): Promise<string[]> {
    const pattern = 'context:farmer:*';
    const keys = await this.redis.keys(pattern);
    return keys.map(key => key.replace('context:farmer:', ''));
  }

  async close() {
    this.redis.disconnect();
  }
}
