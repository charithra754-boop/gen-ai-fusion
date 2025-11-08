import { InvestmentFactors, InvestmentUnitWeights, ProfitDistribution } from './types';

/**
 * Investment Unit Calculator
 * Ensures fair profit distribution in collective farming
 */
export class InvestmentUnitCalculator {
  private readonly DEFAULT_WEIGHTS: InvestmentUnitWeights = {
    land: 0.40,      // Land contribution (largest weight)
    soil: 0.10,      // Soil quality
    inputs: 0.20,    // Seeds, fertilizers, etc.
    labor: 0.15,     // Labor contribution
    water: 0.10,     // Water access/contribution
    equipment: 0.05  // Equipment/machinery
  };

  /**
   * Calculate investment units for a member
   * Higher units = higher profit share
   */
  calculateUnits(
    factors: InvestmentFactors,
    weights?: InvestmentUnitWeights
  ): number {
    const w = weights || this.DEFAULT_WEIGHTS;

    // Normalize each factor to 0-1 scale
    const normalized = {
      land: this.normalizeLand(factors.landArea),
      soil: factors.soilQuality, // Already 0-1
      inputs: this.normalizeInputs(factors.inputsValue),
      labor: this.normalizeLabor(factors.laborDays),
      water: factors.waterAccess, // Already 0-1
      equipment: this.normalizeEquipment(factors.equipmentContribution)
    };

    // Weighted sum
    const score =
      w.land * normalized.land +
      w.soil * normalized.soil +
      w.inputs * normalized.inputs +
      w.labor * normalized.labor +
      w.water * normalized.water +
      w.equipment * normalized.equipment;

    // Scale to units (100 units per full score)
    const units = score * 100;

    console.log(`📊 Investment Units Calculated: ${units.toFixed(2)}`);
    console.log(`   Land: ${factors.landArea} ha (${(normalized.land * 100).toFixed(1)}%)`);
    console.log(`   Inputs: ₹${factors.inputsValue} (${(normalized.inputs * 100).toFixed(1)}%)`);
    console.log(`   Labor: ${factors.laborDays} days (${(normalized.labor * 100).toFixed(1)}%)`);

    return units;
  }

  /**
   * Normalize land area using sigmoid function
   * Prevents extreme values from dominating
   */
  private normalizeLand(area: number): number {
    const avgHolding = 2.0; // Average smallholder land (hectares)
    const k = 1.5; // Steepness factor

    // Sigmoid normalization centered at average
    return 1 / (1 + Math.exp(-k * (area - avgHolding) / avgHolding));
  }

  /**
   * Normalize input value
   * Assumes typical range: ₹20,000 - ₹80,000 per hectare
   */
  private normalizeInputs(value: number): number {
    const minValue = 0;
    const maxValue = 100000; // Upper bound for normalization

    // Linear normalization with cap
    const normalized = (value - minValue) / (maxValue - minValue);
    return Math.min(Math.max(normalized, 0), 1);
  }

  /**
   * Normalize labor contribution
   * Assumes typical range: 20-150 person-days per hectare per season
   */
  private normalizeLabor(days: number): number {
    const minDays = 0;
    const maxDays = 200; // Upper bound for normalization

    const normalized = (days - minDays) / (maxDays - minDays);
    return Math.min(Math.max(normalized, 0), 1);
  }

  /**
   * Normalize equipment value
   * Assumes typical range: ₹0 - ₹200,000
   */
  private normalizeEquipment(value: number): number {
    const maxValue = 200000; // Upper bound

    const normalized = value / maxValue;
    return Math.min(normalized, 1);
  }

  /**
   * Calculate profit distribution for all members
   * Based on their investment units
   */
  distributeProfit(
    totalProfit: number,
    memberUnits: Map<string, { memberId: string; memberName: string; units: number }>,
    deductions: Map<string, number> = new Map()
  ): ProfitDistribution[] {
    // Calculate total units
    const totalUnits = Array.from(memberUnits.values())
      .reduce((sum, m) => sum + m.units, 0);

    if (totalUnits === 0) {
      console.warn('⚠️ No investment units to distribute');
      return [];
    }

    // Calculate distributions
    const distributions: ProfitDistribution[] = [];

    for (const [memberId, member] of memberUnits.entries()) {
      const sharePercentage = (member.units / totalUnits) * 100;
      const grossProfit = (member.units / totalUnits) * totalProfit;
      const memberDeductions = deductions.get(memberId) || 0;
      const netProfit = grossProfit - memberDeductions;

      distributions.push({
        memberId: member.memberId,
        memberName: member.memberName,
        investmentUnits: member.units,
        sharePercentage,
        grossProfit,
        deductions: memberDeductions,
        netProfit
      });

      console.log(`💰 ${member.memberName}: ${sharePercentage.toFixed(2)}% = ₹${netProfit.toFixed(2)}`);
    }

    // Sort by net profit (descending)
    distributions.sort((a, b) => b.netProfit - a.netProfit);

    return distributions;
  }

  /**
   * Validate investment factors
   * Ensures all inputs are reasonable
   */
  validateFactors(factors: InvestmentFactors): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (factors.landArea <= 0) {
      errors.push('Land area must be positive');
    }

    if (factors.landArea > 100) {
      errors.push('Land area seems too large for smallholder (>100 ha)');
    }

    if (factors.soilQuality < 0 || factors.soilQuality > 1) {
      errors.push('Soil quality must be between 0 and 1');
    }

    if (factors.inputsValue < 0) {
      errors.push('Inputs value cannot be negative');
    }

    if (factors.laborDays < 0) {
      errors.push('Labor days cannot be negative');
    }

    if (factors.waterAccess < 0 || factors.waterAccess > 1) {
      errors.push('Water access must be between 0 and 1');
    }

    if (factors.equipmentContribution < 0) {
      errors.push('Equipment contribution cannot be negative');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Calculate units with detailed breakdown
   * Useful for transparency and member education
   */
  calculateUnitsWithBreakdown(
    factors: InvestmentFactors,
    weights?: InvestmentUnitWeights
  ): {
    totalUnits: number;
    breakdown: {
      factor: string;
      contribution: number;
      weight: number;
      units: number;
    }[];
  } {
    const w = weights || this.DEFAULT_WEIGHTS;

    const normalized = {
      land: this.normalizeLand(factors.landArea),
      soil: factors.soilQuality,
      inputs: this.normalizeInputs(factors.inputsValue),
      labor: this.normalizeLabor(factors.laborDays),
      water: factors.waterAccess,
      equipment: this.normalizeEquipment(factors.equipmentContribution)
    };

    const breakdown = [
      {
        factor: 'Land Area',
        contribution: normalized.land,
        weight: w.land,
        units: normalized.land * w.land * 100
      },
      {
        factor: 'Soil Quality',
        contribution: normalized.soil,
        weight: w.soil,
        units: normalized.soil * w.soil * 100
      },
      {
        factor: 'Inputs (Seeds, Fertilizers)',
        contribution: normalized.inputs,
        weight: w.inputs,
        units: normalized.inputs * w.inputs * 100
      },
      {
        factor: 'Labor Contribution',
        contribution: normalized.labor,
        weight: w.labor,
        units: normalized.labor * w.labor * 100
      },
      {
        factor: 'Water Access',
        contribution: normalized.water,
        weight: w.water,
        units: normalized.water * w.water * 100
      },
      {
        factor: 'Equipment',
        contribution: normalized.equipment,
        weight: w.equipment,
        units: normalized.equipment * w.equipment * 100
      }
    ];

    const totalUnits = breakdown.reduce((sum, b) => sum + b.units, 0);

    return { totalUnits, breakdown };
  }

  /**
   * Suggest optimal Investment Unit weights for an FPO
   * Based on local conditions and resource availability
   */
  suggestWeights(fpoContext: {
    avgLandSize: number;
    waterScarcity: boolean;
    mechanizationLevel: 'low' | 'medium' | 'high';
    primaryCostDriver: 'land' | 'inputs' | 'labor';
  }): InvestmentUnitWeights {
    const weights = { ...this.DEFAULT_WEIGHTS };

    // In water-scarce regions, increase water weight
    if (fpoContext.waterScarcity) {
      weights.water = 0.15;
      weights.land = 0.35; // Reduce land slightly
    }

    // In highly mechanized regions, increase equipment weight
    if (fpoContext.mechanizationLevel === 'high') {
      weights.equipment = 0.10;
      weights.labor = 0.10; // Reduce labor
    }

    // Emphasize primary cost driver
    if (fpoContext.primaryCostDriver === 'inputs') {
      weights.inputs = 0.25;
      weights.land = 0.35;
    } else if (fpoContext.primaryCostDriver === 'labor') {
      weights.labor = 0.20;
      weights.inputs = 0.15;
    }

    // Normalize to sum to 1.0
    const sum = Object.values(weights).reduce((a, b) => a + b, 0);
    Object.keys(weights).forEach(key => {
      weights[key as keyof InvestmentUnitWeights] /= sum;
    });

    console.log('💡 Suggested Investment Unit Weights:');
    console.log(`   Land: ${(weights.land * 100).toFixed(1)}%`);
    console.log(`   Inputs: ${(weights.inputs * 100).toFixed(1)}%`);
    console.log(`   Labor: ${(weights.labor * 100).toFixed(1)}%`);
    console.log(`   Water: ${(weights.water * 100).toFixed(1)}%`);
    console.log(`   Equipment: ${(weights.equipment * 100).toFixed(1)}%`);

    return weights;
  }
}
