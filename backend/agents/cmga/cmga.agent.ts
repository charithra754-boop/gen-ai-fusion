import { BaseAgent } from '../base/agent.base';
import {
  MCPMessage,
  AgentType,
  MessageType,
  AgentCapability
} from '../../mcp-bus/src/protocols/mcp.protocol';
import { PortfolioOptimizer } from './portfolio-optimizer';
import { InvestmentUnitCalculator } from './investment-calculator';
import {
  CropOption,
  PortfolioConstraints,
  MarketData,
  ClimateData,
  YieldData,
  InvestmentFactors,
  ProfitDistribution
} from './types';

/**
 * Collective Market Governance Agent (CMGA)
 *
 * The TRANSFORMATIVE agent that enables collective action:
 * - Strategic portfolio planning for FPOs
 * - Transparent Investment Unit tracking
 * - Automated profit distribution
 * - Risk-adjusted crop diversification
 */
export class CMGAAgent extends BaseAgent {
  private portfolioOptimizer: PortfolioOptimizer;
  private investmentCalculator: InvestmentUnitCalculator;

  constructor(messageBus: any, contextManager: any) {
    super(AgentType.CMGA, messageBus, contextManager);
    this.portfolioOptimizer = new PortfolioOptimizer();
    this.investmentCalculator = new InvestmentUnitCalculator();
  }

  protected defineCapabilities(): AgentCapability {
    return {
      agentType: AgentType.CMGA,
      version: '1.0.0',
      capabilities: [
        'collective-portfolio-planning',
        'investment-unit-calculation',
        'profit-distribution',
        'risk-assessment',
        'diversification-analysis'
      ],
      inputSchemas: {
        planPortfolio: {
          fpoId: 'string',
          season: 'string',
          year: 'number',
          constraints: 'PortfolioConstraints',
          cropOptions: 'CropOption[]'
        },
        calculateInvestmentUnits: {
          fpoId: 'string',
          memberId: 'string',
          factors: 'InvestmentFactors'
        },
        distributeProfits: {
          fpoId: 'string',
          portfolioId: 'string',
          totalRevenue: 'number'
        },
        getFPOInsights: {
          fpoId: 'string'
        }
      },
      outputSchemas: {
        portfolio: 'OptimizedPortfolio',
        investmentUnits: 'number',
        profitDistributions: 'ProfitDistribution[]'
      },
      dependencies: [AgentType.MIA, AgentType.GAA, AgentType.CRA]
    };
  }

  protected async handleMessage(message: MCPMessage): Promise<any> {
    const { payload } = message;

    this.log(`Handling action: ${payload.action}`);

    try {
      switch (payload.action) {
        case 'planPortfolio':
          return await this.planCollectivePortfolio(payload.data);

        case 'calculateInvestmentUnits':
          return await this.calculateInvestmentUnits(payload.data);

        case 'distributeProfits':
          return await this.distributeProfit(payload.data);

        case 'getFPOInsights':
          return await this.getFPOInsights(payload.data);

        case 'suggestWeights':
          return await this.suggestInvestmentWeights(payload.data);

        case 'validateFactors':
          return this.investmentCalculator.validateFactors(payload.data.factors);

        default:
          throw new Error(`Unknown action: ${payload.action}`);
      }
    } catch (error: any) {
      this.log(`Error: ${error.message}`, { error: error.stack });
      throw error;
    }
  }

  /**
   * Plan collective portfolio for an FPO
   * Integrates data from MIA, GAA, and CRA
   */
  private async planCollectivePortfolio(data: {
    fpoId: string;
    season: string;
    year: number;
    constraints: PortfolioConstraints;
    cropOptions: CropOption[];
  }): Promise<any> {
    this.log('📊 Planning collective portfolio', {
      fpoId: data.fpoId,
      season: data.season,
      crops: data.cropOptions.length
    });

    // Get FPO context
    const fpoContext = await this.getContext(undefined, data.fpoId);

    // Request market intelligence from MIA
    this.log('📡 Requesting market data from MIA...');
    const marketData: MarketData = await this.requestFromAgent(
      AgentType.MIA,
      {
        action: 'getPriceForecast',
        crops: data.cropOptions.map(c => c.name),
        season: data.season
      },
      { fpoId: data.fpoId }
    ).catch(() => this.getMockMarketData(data.cropOptions));

    // Request climate resilience from CRA
    this.log('📡 Requesting climate data from CRA...');
    const climateData: ClimateData = await this.requestFromAgent(
      AgentType.CRA,
      {
        action: 'getClimateResilience',
        location: fpoContext.location,
        season: data.season
      },
      { fpoId: data.fpoId }
    ).catch(() => this.getMockClimateData(data.cropOptions));

    // Request yield forecast from GAA
    this.log('📡 Requesting yield forecasts from GAA...');
    const yieldData: YieldData = await this.requestFromAgent(
      AgentType.GAA,
      {
        action: 'forecastYield',
        crops: data.cropOptions.map(c => c.name),
        season: data.season,
        location: fpoContext.location
      },
      { fpoId: data.fpoId }
    ).catch(() => this.getMockYieldData(data.cropOptions));

    // Optimize portfolio
    this.log('🎯 Optimizing portfolio...');
    const optimizedPortfolio = await this.portfolioOptimizer.optimize(
      data.constraints,
      data.cropOptions,
      marketData,
      climateData,
      yieldData
    );

    // Store portfolio in context
    await this.contextManager.updateFPOContext(data.fpoId, {
      currentPortfolio: optimizedPortfolio,
      season: data.season,
      year: data.year,
      updatedAt: new Date()
    });

    // Broadcast portfolio update event
    await this.broadcast(
      {
        event: 'portfolio-created',
        fpoId: data.fpoId,
        portfolioId: `${data.fpoId}-${data.season}-${data.year}`,
        crops: optimizedPortfolio.crops.map(c => c.cropName),
        expectedReturn: optimizedPortfolio.expectedReturn,
        risk: optimizedPortfolio.portfolioRisk
      },
      { fpoId: data.fpoId }
    );

    this.log('✅ Portfolio planning complete', {
      crops: optimizedPortfolio.crops.length,
      expectedReturn: `${(optimizedPortfolio.expectedReturn * 100).toFixed(2)}%`,
      sharpeRatio: optimizedPortfolio.sharpeRatio.toFixed(2)
    });

    return {
      success: true,
      portfolio: optimizedPortfolio,
      portfolioId: `${data.fpoId}-${data.season}-${data.year}`,
      recommendations: this.generateRecommendations(optimizedPortfolio)
    };
  }

  /**
   * Calculate Investment Units for a member
   */
  private async calculateInvestmentUnits(data: {
    fpoId: string;
    memberId: string;
    factors: InvestmentFactors;
    weights?: any;
  }): Promise<any> {
    this.log('💰 Calculating Investment Units', {
      fpoId: data.fpoId,
      memberId: data.memberId
    });

    // Validate factors
    const validation = this.investmentCalculator.validateFactors(data.factors);
    if (!validation.valid) {
      throw new Error(`Invalid factors: ${validation.errors.join(', ')}`);
    }

    // Calculate units with breakdown
    const result = this.investmentCalculator.calculateUnitsWithBreakdown(
      data.factors,
      data.weights
    );

    // Store in context
    await this.contextManager.updateFPOContext(data.fpoId, {
      memberUnits: {
        [data.memberId]: {
          units: result.totalUnits,
          factors: data.factors,
          calculatedAt: new Date()
        }
      }
    });

    this.log('✅ Investment Units calculated', {
      totalUnits: result.totalUnits.toFixed(2)
    });

    return {
      success: true,
      memberId: data.memberId,
      totalUnits: result.totalUnits,
      breakdown: result.breakdown
    };
  }

  /**
   * Distribute profits among FPO members
   */
  private async distributeProfit(data: {
    fpoId: string;
    portfolioId: string;
    totalRevenue: number;
    costs?: number;
    deductions?: Map<string, number>;
  }): Promise<any> {
    this.log('💸 Distributing profits', {
      fpoId: data.fpoId,
      portfolioId: data.portfolioId,
      totalRevenue: data.totalRevenue
    });

    // Get FPO context with member units
    const fpoContext = await this.contextManager.getFPOContext(data.fpoId);
    const memberUnits = fpoContext.memberUnits || {};

    // Convert to Map format
    const unitsMap = new Map(
      Object.entries(memberUnits).map(([id, data]: [string, any]) => [
        id,
        { memberId: id, memberName: data.name || id, units: data.units }
      ])
    );

    // Calculate total profit
    const totalCosts = data.costs || 0;
    const totalProfit = data.totalRevenue - totalCosts;

    if (totalProfit <= 0) {
      this.log('⚠️ No profit to distribute');
      return {
        success: false,
        error: 'No profit available for distribution',
        totalRevenue: data.totalRevenue,
        totalCosts,
        totalProfit
      };
    }

    // Distribute profits
    const distributions = this.investmentCalculator.distributeProfit(
      totalProfit,
      unitsMap,
      data.deductions
    );

    // Store distributions in context
    await this.contextManager.updateFPOContext(data.fpoId, {
      latestDistribution: {
        portfolioId: data.portfolioId,
        totalRevenue: data.totalRevenue,
        totalCosts,
        totalProfit,
        distributions,
        distributedAt: new Date()
      }
    });

    // Broadcast distribution event
    await this.broadcast(
      {
        event: 'profit-distributed',
        fpoId: data.fpoId,
        portfolioId: data.portfolioId,
        totalProfit,
        memberCount: distributions.length
      },
      { fpoId: data.fpoId }
    );

    this.log('✅ Profit distribution complete', {
      members: distributions.length,
      totalProfit: `₹${totalProfit.toFixed(2)}`
    });

    return {
      success: true,
      totalRevenue: data.totalRevenue,
      totalCosts,
      totalProfit,
      distributions,
      summary: {
        highestShare: distributions[0],
        lowestShare: distributions[distributions.length - 1],
        averageShare: totalProfit / distributions.length
      }
    };
  }

  /**
   * Get comprehensive insights for an FPO
   */
  private async getFPOInsights(data: { fpoId: string }): Promise<any> {
    this.log('📈 Generating FPO insights', { fpoId: data.fpoId });

    const fpoContext = await this.contextManager.getFPOContext(data.fpoId);

    const insights = {
      fpoId: data.fpoId,
      currentPortfolio: fpoContext.currentPortfolio || null,
      memberCount: Object.keys(fpoContext.memberUnits || {}).length,
      latestDistribution: fpoContext.latestDistribution || null,
      performance: this.calculatePerformance(fpoContext),
      recommendations: this.generateFPORecommendations(fpoContext)
    };

    return insights;
  }

  /**
   * Suggest optimal Investment Unit weights for an FPO
   */
  private async suggestInvestmentWeights(data: {
    fpoId: string;
    avgLandSize?: number;
    waterScarcity?: boolean;
    mechanizationLevel?: 'low' | 'medium' | 'high';
    primaryCostDriver?: 'land' | 'inputs' | 'labor';
  }): Promise<any> {
    const weights = this.investmentCalculator.suggestWeights({
      avgLandSize: data.avgLandSize || 2.0,
      waterScarcity: data.waterScarcity || false,
      mechanizationLevel: data.mechanizationLevel || 'low',
      primaryCostDriver: data.primaryCostDriver || 'land'
    });

    return {
      success: true,
      weights,
      explanation: this.explainWeights(weights)
    };
  }

  /**
   * Generate portfolio recommendations
   */
  private generateRecommendations(portfolio: any): string[] {
    const recommendations: string[] = [];

    if (portfolio.sharpeRatio < 0.5) {
      recommendations.push('⚠️ Low risk-adjusted return. Consider diversifying further.');
    } else if (portfolio.sharpeRatio > 1.5) {
      recommendations.push('✅ Excellent risk-adjusted return!');
    }

    if (portfolio.diversificationIndex < 0.5) {
      recommendations.push('⚠️ Portfolio is concentrated. Add more crop varieties to reduce risk.');
    } else if (portfolio.diversificationIndex > 0.8) {
      recommendations.push('✅ Well-diversified portfolio!');
    }

    if (portfolio.utilizationRates.water > 90) {
      recommendations.push('⚠️ High water usage. Consider adding drought-resistant crops.');
    }

    if (portfolio.utilizationRates.land < 70) {
      recommendations.push('💡 Land is underutilized. Consider adding another crop.');
    }

    return recommendations;
  }

  /**
   * Calculate FPO performance metrics
   */
  private calculatePerformance(fpoContext: any): any {
    if (!fpoContext.latestDistribution) {
      return { message: 'No distribution data available yet' };
    }

    const dist = fpoContext.latestDistribution;
    return {
      totalRevenue: dist.totalRevenue,
      totalProfit: dist.totalProfit,
      profitMargin: (dist.totalProfit / dist.totalRevenue) * 100,
      memberCount: dist.distributions?.length || 0,
      averageProfit: dist.totalProfit / (dist.distributions?.length || 1)
    };
  }

  /**
   * Generate FPO-level recommendations
   */
  private generateFPORecommendations(fpoContext: any): string[] {
    const recommendations: string[] = [];

    if (!fpoContext.currentPortfolio) {
      recommendations.push('📊 Create your first collective portfolio to get started');
    }

    if (fpoContext.memberCount < 10) {
      recommendations.push('👥 Recruit more members to increase collective bargaining power');
    }

    if (fpoContext.currentPortfolio?.sharpeRatio < 1.0) {
      recommendations.push('📈 Review portfolio to improve risk-adjusted returns');
    }

    return recommendations;
  }

  /**
   * Explain Investment Unit weights
   */
  private explainWeights(weights: any): string {
    const explanations: string[] = [];

    if (weights.land > 0.35) {
      explanations.push('Land is the primary factor (typical for land-based cooperatives)');
    }

    if (weights.inputs > 0.2) {
      explanations.push('Inputs weighted highly (important for intensive farming)');
    }

    if (weights.water > 0.12) {
      explanations.push('Water access is critical (water-scarce region)');
    }

    return explanations.join('. ');
  }

  // Mock data methods (for when other agents aren't available yet)

  private getMockMarketData(crops: CropOption[]): MarketData {
    const data: MarketData = {
      priceForecast: {},
      volatility: {},
      demandIndex: {},
      priceHistory: {}
    };

    crops.forEach(crop => {
      data.priceForecast[crop.name] = crop.avgPrice * (1 + Math.random() * 0.2 - 0.1);
      data.volatility[crop.name] = 0.15 + Math.random() * 0.15;
      data.demandIndex[crop.name] = Math.random();
    });

    return data;
  }

  private getMockClimateData(crops: CropOption[]): ClimateData {
    const data: ClimateData = {
      riskScore: {},
      waterAvailability: 0.7,
      temperatureForecast: {
        min: 20,
        max: 35,
        avgRainfall: 800
      },
      anomalyDetected: false
    };

    crops.forEach(crop => {
      data.riskScore[crop.name] = Math.random() * 0.5;
    });

    return data;
  }

  private getMockYieldData(crops: CropOption[]): YieldData {
    const data: YieldData = {};

    crops.forEach(crop => {
      data[crop.name] = {
        predicted: crop.avgYield * (1 + Math.random() * 0.2 - 0.1),
        confidence: 0.7 + Math.random() * 0.2,
        historicalAvg: crop.avgYield
      };
    });

    return data;
  }
}
