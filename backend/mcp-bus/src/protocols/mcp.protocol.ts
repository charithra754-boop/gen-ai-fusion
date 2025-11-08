/**
 * Model Context Protocol (MCP) Implementation
 * Enables efficient, context-aware communication between agents in KisaanMitra
 */

export enum MessageType {
  REQUEST = 'request',
  RESPONSE = 'response',
  EVENT = 'event',
  CONTEXT_UPDATE = 'context_update',
  BROADCAST = 'broadcast'
}

export enum AgentType {
  CMGA = 'collective-market-governance',
  CRA = 'climate-resource',
  GAA = 'geo-agronomy',
  FIA = 'financial-inclusion',
  MIA = 'market-intelligence',
  LIA = 'logistics-infrastructure',
  HIA = 'human-interface'
}

export interface MCPMessage {
  id: string;
  type: MessageType;
  source: AgentType;
  target?: AgentType | AgentType[];
  timestamp: Date;
  payload: any;
  context?: MessageContext;
  priority: MessagePriority;
  ttl?: number; // Time-to-live in seconds
}

export interface MessageContext {
  farmerId?: string;
  fpoId?: string;
  location?: GeoLocation;
  cropType?: string;
  season?: string;
  previousMessages?: string[]; // IDs of related messages
  metadata?: Record<string, any>;
}

export interface GeoLocation {
  latitude: number;
  longitude: number;
  accuracy?: number;
  village?: string;
  district?: string;
  state?: string;
}

export enum MessagePriority {
  LOW = 0,
  NORMAL = 1,
  HIGH = 2,
  CRITICAL = 3
}

export interface AgentCapability {
  agentType: AgentType;
  version: string;
  capabilities: string[];
  inputSchemas: Record<string, any>;
  outputSchemas: Record<string, any>;
  dependencies: AgentType[];
}

export interface ContextState {
  farmContext?: FarmContext;
  marketContext?: MarketContext;
  weatherContext?: WeatherContext;
  fpoContext?: FPOContext;
}

export interface FarmContext {
  farmerId: string;
  fieldBoundaries?: any;
  soilData?: any;
  cropHistory?: any;
  currentCrops?: any;
}

export interface MarketContext {
  currentPrices?: any;
  demandForecast?: any;
  inventoryLevel?: number;
}

export interface WeatherContext {
  current?: any;
  forecast?: any;
  historicalAnomaly?: boolean;
}

export interface FPOContext {
  fpoId: string;
  members?: string[];
  collectivePortfolio?: any;
  investmentUnits?: Map<string, number>;
}
