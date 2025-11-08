import {
  PortfolioConstraints,
  CropOption,
  OptimizedPortfolio,
  CropAllocation,
  MarketData,
  ClimateData,
  YieldData
} from './types';

/**
 * Portfolio Optimization Engine for Collective Crop Planning
 * Uses Modern Portfolio Theory adapted for agriculture
 */
export class PortfolioOptimizer {
  /**
   * Main optimization function
   * Maximizes expected return while minimizing risk
   */
  async optimize(
    constraints: PortfolioConstraints,
    cropOptions: CropOption[],
    marketData: MarketData,
    climateData: ClimateData,
    yieldForecasts: YieldData
  ): Promise<OptimizedPortfolio> {
    console.log('🎯 Starting portfolio optimization...');

    // Step 1: Calculate expected returns for each crop
    const returns = cropOptions.map(crop =>
      this.calculateExpectedReturn(crop, marketData, yieldForecasts)
    );

    // Step 2: Calculate risk (variance) for each crop
    const risks = cropOptions.map(crop =>
      this.calculateRisk(crop, climateData, marketData)
    );

    // Step 3: Calculate correlation matrix
    const correlationMatrix = this.calculateCorrelations(cropOptions, marketData);

    // Step 4: Optimize allocation
    const allocation = await this.solveOptimization(
      cropOptions,
      returns,
      risks,
      correlationMatrix,
      constraints
    );

    // Step 5: Calculate portfolio metrics
    const portfolioReturn = this.calculatePortfolioReturn(allocation, returns);
    const portfolioRisk = this.calculatePortfolioRisk(allocation, risks, correlationMatrix);
    const sharpeRatio = this.calculateSharpeRatio(portfolioReturn, portfolioRisk);
    const diversificationIndex = this.calculateDiversification(allocation);

    // Step 6: Calculate resource utilization
    const totalWater = allocation.reduce((sum, a) => sum + a.waterNeeded, 0);
    const totalLabor = allocation.reduce((sum, a) => sum + a.laborNeeded, 0);
    const totalCost = allocation.reduce((sum, a) => sum + a.costRequired, 0);
    const totalLand = allocation.reduce((sum, a) => sum + a.landArea, 0);

    console.log('✅ Portfolio optimization complete');
    console.log(`   Expected Return: ${(portfolioReturn * 100).toFixed(2)}%`);
    console.log(`   Risk (Std Dev): ${(portfolioRisk * 100).toFixed(2)}%`);
    console.log(`   Sharpe Ratio: ${sharpeRatio.toFixed(2)}`);
    console.log(`   Diversification: ${(diversificationIndex * 100).toFixed(2)}%`);

    return {
      crops: allocation,
      expectedReturn: portfolioReturn,
      portfolioRisk,
      sharpeRatio,
      diversificationIndex,
      totalWaterUsage: totalWater,
      totalLaborUsage: totalLabor,
      totalCostRequired: totalCost,
      utilizationRates: {
        land: (totalLand / constraints.totalLand) * 100,
        water: (totalWater / constraints.totalWater) * 100,
        labor: (totalLabor / constraints.totalLabor) * 100,
        budget: (totalCost / constraints.totalBudget) * 100
      }
    };
  }

  /**
   * Calculate expected return for a crop
   * Return = (Expected Revenue - Cost) / Cost
   */
  private calculateExpectedReturn(
    crop: CropOption,
    market: MarketData,
    yieldForecasts: YieldData
  ): number {
    // Use yield forecast if available, otherwise use average
    const predictedYield = yieldForecasts[crop.name]?.predicted || crop.avgYield;

    // Use market price forecast if available, otherwise use average
    const predictedPrice = market.priceForecast[crop.name] || crop.avgPrice;

    // Expected revenue per hectare
    const revenue = predictedYield * predictedPrice;

    // Return on investment
    const roi = (revenue - crop.cultivationCost) / crop.cultivationCost;

    return roi;
  }

  /**
   * Calculate risk for a crop
   * Risk = weighted combination of price volatility, yield variability, and climate risk
   */
  private calculateRisk(
    crop: CropOption,
    climate: ClimateData,
    market: MarketData
  ): number {
    // Price volatility (coefficient of variation)
    const priceVolatility = market.volatility[crop.name] || 0.2;

    // Yield variability
    const yieldVariability = crop.yieldStdDev / crop.avgYield;

    // Climate vulnerability
    const climateRisk = climate.riskScore[crop.name] || 0.5;

    // Weighted combination (40% price, 40% yield, 20% climate)
    const totalRisk = 0.4 * priceVolatility + 0.4 * yieldVariability + 0.2 * climateRisk;

    return totalRisk;
  }

  /**
   * Calculate correlation matrix between crops
   * Crops in same family or season tend to be correlated
   */
  private calculateCorrelations(crops: CropOption[], market: MarketData): number[][] {
    const n = crops.length;
    const matrix: number[][] = Array(n).fill(null).map(() => Array(n).fill(0));

    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        if (i === j) {
          matrix[i][j] = 1.0; // Perfect correlation with itself
        } else {
          matrix[i][j] = this.estimateCorrelation(crops[i], crops[j], market);
        }
      }
    }

    return matrix;
  }

  /**
   * Estimate correlation between two crops
   */
  private estimateCorrelation(
    crop1: CropOption,
    crop2: CropOption,
    market: MarketData
  ): number {
    // If we have historical price data, calculate actual correlation
    if (market.priceHistory?.[crop1.name] && market.priceHistory?.[crop2.name]) {
      return this.calculatePriceCorrelation(
        market.priceHistory[crop1.name],
        market.priceHistory[crop2.name]
      );
    }

    // Otherwise, use heuristics
    let correlation = 0.1; // Base correlation

    // Same family crops are highly correlated
    if (crop1.family === crop2.family) {
      correlation += 0.5;
    }

    // Same season crops are moderately correlated
    if (crop1.season === crop2.season) {
      correlation += 0.3;
    }

    // Similar water requirements indicate similar climate dependency
    const waterDiff = Math.abs(crop1.waterRequirement - crop2.waterRequirement);
    const maxWater = Math.max(crop1.waterRequirement, crop2.waterRequirement);
    if (maxWater > 0 && waterDiff / maxWater < 0.2) {
      correlation += 0.2;
    }

    return Math.min(correlation, 0.9); // Cap at 0.9
  }

  /**
   * Calculate actual correlation from historical price data
   */
  private calculatePriceCorrelation(prices1: number[], prices2: number[]): number {
    const n = Math.min(prices1.length, prices2.length);
    if (n < 2) return 0.5;

    // Calculate means
    const mean1 = prices1.slice(0, n).reduce((a, b) => a + b, 0) / n;
    const mean2 = prices2.slice(0, n).reduce((a, b) => a + b, 0) / n;

    // Calculate covariance and standard deviations
    let covariance = 0;
    let variance1 = 0;
    let variance2 = 0;

    for (let i = 0; i < n; i++) {
      const diff1 = prices1[i] - mean1;
      const diff2 = prices2[i] - mean2;
      covariance += diff1 * diff2;
      variance1 += diff1 * diff1;
      variance2 += diff2 * diff2;
    }

    const stdDev1 = Math.sqrt(variance1 / n);
    const stdDev2 = Math.sqrt(variance2 / n);

    if (stdDev1 === 0 || stdDev2 === 0) return 0;

    return covariance / (n * stdDev1 * stdDev2);
  }

  /**
   * Solve optimization problem
   * This is a simplified heuristic approach
   * For production, use proper quadratic programming solver
   */
  private async solveOptimization(
    crops: CropOption[],
    returns: number[],
    risks: number[],
    correlations: number[][],
    constraints: PortfolioConstraints
  ): Promise<CropAllocation[]> {
    // Calculate Sharpe ratio for each crop
    const riskFreeRate = 0.05; // 5% assumption
    const sharpeRatios = returns.map((r, i) => ({
      index: i,
      crop: crops[i],
      return: r,
      risk: risks[i],
      sharpe: (r - riskFreeRate) / risks[i]
    }));

    // Sort by Sharpe ratio (risk-adjusted return)
    sharpeRatios.sort((a, b) => b.sharpe - a.sharpe);

    // Greedy allocation with constraints
    const allocation: CropAllocation[] = [];
    let remainingLand = constraints.totalLand;
    let remainingWater = constraints.totalWater;
    let remainingLabor = constraints.totalLabor;
    let remainingBudget = constraints.totalBudget;

    // Ensure minimum diversity
    const minCrops = Math.min(
      constraints.minCropDiversity || 3,
      crops.length
    );

    for (let i = 0; i < sharpeRatios.length && allocation.length < minCrops; i++) {
      const { index, crop, return: ret, risk } = sharpeRatios[i];

      // Calculate maximum allocation for this crop
      const maxLandByCrop = remainingLand * 0.4; // Max 40% in single crop
      const maxLandByWater = remainingWater / crop.waterRequirement;
      const maxLandByLabor = remainingLabor / crop.laborDays;
      const maxLandByBudget = remainingBudget / crop.cultivationCost;

      const allocatedLand = Math.min(
        maxLandByCrop,
        maxLandByWater,
        maxLandByLabor,
        maxLandByBudget,
        remainingLand / minCrops // Ensure enough land for minimum diversity
      );

      if (allocatedLand > 0.1) { // Minimum 0.1 hectare
        const waterNeeded = allocatedLand * crop.waterRequirement;
        const laborNeeded = allocatedLand * crop.laborDays;
        const costRequired = allocatedLand * crop.cultivationCost;

        allocation.push({
          cropIndex: index,
          cropName: crop.name,
          landArea: allocatedLand,
          expectedReturn: ret,
          risk,
          waterNeeded,
          laborNeeded,
          costRequired
        });

        remainingLand -= allocatedLand;
        remainingWater -= waterNeeded;
        remainingLabor -= laborNeeded;
        remainingBudget -= costRequired;
      }
    }

    // Allocate remaining land if still available and within constraints
    if (remainingLand > 0.5) {
      for (const { index, crop, return: ret, risk } of sharpeRatios) {
        if (allocation.find(a => a.cropIndex === index)) continue; // Skip already allocated

        const maxLand = Math.min(
          remainingLand * 0.3,
          remainingWater / crop.waterRequirement,
          remainingLabor / crop.laborDays,
          remainingBudget / crop.cultivationCost
        );

        if (maxLand > 0.1) {
          const waterNeeded = maxLand * crop.waterRequirement;
          const laborNeeded = maxLand * crop.laborDays;
          const costRequired = maxLand * crop.cultivationCost;

          allocation.push({
            cropIndex: index,
            cropName: crop.name,
            landArea: maxLand,
            expectedReturn: ret,
            risk,
            waterNeeded,
            laborNeeded,
            costRequired
          });

          remainingLand -= maxLand;
          remainingWater -= waterNeeded;
          remainingLabor -= laborNeeded;
          remainingBudget -= costRequired;

          if (remainingLand < 0.5) break;
        }
      }
    }

    return allocation;
  }

  /**
   * Calculate portfolio expected return
   * Weighted average of individual returns
   */
  private calculatePortfolioReturn(allocation: CropAllocation[], returns: number[]): number {
    const totalLand = allocation.reduce((sum, a) => sum + a.landArea, 0);
    if (totalLand === 0) return 0;

    return allocation.reduce((sum, a) => {
      const weight = a.landArea / totalLand;
      return sum + weight * returns[a.cropIndex];
    }, 0);
  }

  /**
   * Calculate portfolio risk (standard deviation)
   * Uses portfolio variance formula accounting for correlations
   */
  private calculatePortfolioRisk(
    allocation: CropAllocation[],
    risks: number[],
    correlations: number[][]
  ): number {
    const totalLand = allocation.reduce((sum, a) => sum + a.landArea, 0);
    if (totalLand === 0) return 0;

    let variance = 0;

    for (let i = 0; i < allocation.length; i++) {
      for (let j = 0; j < allocation.length; j++) {
        const wi = allocation[i].landArea / totalLand;
        const wj = allocation[j].landArea / totalLand;
        const corr = correlations[allocation[i].cropIndex][allocation[j].cropIndex];

        variance += wi * wj * risks[allocation[i].cropIndex] *
                   risks[allocation[j].cropIndex] * corr;
      }
    }

    return Math.sqrt(variance);
  }

  /**
   * Calculate Sharpe ratio (risk-adjusted return)
   */
  private calculateSharpeRatio(portfolioReturn: number, portfolioRisk: number): number {
    const riskFreeRate = 0.05; // 5% assumption
    if (portfolioRisk === 0) return 0;

    return (portfolioReturn - riskFreeRate) / portfolioRisk;
  }

  /**
   * Calculate diversification index (Herfindahl index)
   * 1 = perfectly diversified, 0 = concentrated in one crop
   */
  private calculateDiversification(allocation: CropAllocation[]): number {
    const totalLand = allocation.reduce((sum, a) => sum + a.landArea, 0);
    if (totalLand === 0) return 0;

    const sumSquares = allocation.reduce((sum, a) => {
      const weight = a.landArea / totalLand;
      return sum + weight * weight;
    }, 0);

    // Normalized Herfindahl: (1 - H) / (1 - 1/n)
    const n = allocation.length;
    if (n === 1) return 0;

    return (1 - sumSquares) / (1 - 1 / n);
  }
}
