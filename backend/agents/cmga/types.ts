/**
 * Type definitions for CMGA (Collective Market Governance Agent)
 */

export interface CropOption {
  name: string;
  family: string; // e.g., "solanaceae", "legume"
  season: string; // "kharif", "rabi", "zaid"
  avgYield: number; // quintals per hectare
  yieldStdDev: number; // standard deviation
  avgPrice: number; // ₹ per quintal
  cultivationCost: number; // ₹ per hectare
  waterRequirement: number; // cubic meters per hectare
  laborDays: number; // person-days per hectare
  growingDuration: number; // days
  soilTypes: string[]; // ["loamy", "clay", etc.]
  minTemp: number; // °C
  maxTemp: number; // °C
}

export interface PortfolioConstraints {
  totalLand: number; // hectares
  totalWater: number; // cubic meters
  totalLabor: number; // person-days available
  totalBudget: number; // ₹
  maxCropDiversity: number; // minimum number of different crops
  minCropDiversity: number;
  riskTolerance: number; // 0-1, higher = more risk acceptable
}

export interface CropAllocation {
  cropIndex: number;
  cropName: string;
  landArea: number; // hectares
  expectedReturn: number; // percentage
  risk: number; // 0-1
  waterNeeded: number; // cubic meters
  laborNeeded: number; // person-days
  costRequired: number; // ₹
  assignedFarmers?: string[]; // farmer IDs
}

export interface OptimizedPortfolio {
  crops: CropAllocation[];
  expectedReturn: number; // weighted portfolio return %
  portfolioRisk: number; // portfolio standard deviation
  sharpeRatio: number; // return/risk ratio
  diversificationIndex: number; // 0-1, higher = more diversified
  totalWaterUsage: number;
  totalLaborUsage: number;
  totalCostRequired: number;
  utilizationRates: {
    land: number; // %
    water: number; // %
    labor: number; // %
    budget: number; // %
  };
}

export interface InvestmentFactors {
  landArea: number; // hectares
  soilQuality: number; // 0-1 score
  inputsValue: number; // ₹ value of seeds, fertilizers
  laborDays: number; // contributed labor
  waterAccess: number; // 0-1 score (well, canal, etc.)
  equipmentContribution: number; // ₹ value
}

export interface InvestmentUnitWeights {
  land: number;
  soil: number;
  inputs: number;
  labor: number;
  water: number;
  equipment: number;
}

export interface ProfitDistribution {
  memberId: string;
  memberName: string;
  investmentUnits: number;
  sharePercentage: number;
  grossProfit: number;
  deductions: number;
  netProfit: number;
}

export interface MarketData {
  priceForecast: Record<string, number>; // crop -> predicted price
  volatility: Record<string, number>; // crop -> price volatility
  demandIndex: Record<string, number>; // crop -> demand score 0-1
  priceHistory: Record<string, number[]>; // crop -> historical prices
}

export interface ClimateData {
  riskScore: Record<string, number>; // crop -> climate risk 0-1
  waterAvailability: number; // 0-1 score
  temperatureForecast: {
    min: number;
    max: number;
    avgRainfall: number;
  };
  anomalyDetected: boolean;
}

export interface YieldData {
  [crop: string]: {
    predicted: number; // quintals/ha
    confidence: number; // 0-1
    historicalAvg: number;
  };
}
