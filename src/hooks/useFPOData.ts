import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { supabase } from '@/integrations/supabase/client';

/**
 * Custom hooks for FPO (Farmer Producer Organization) data management
 * Integrates with CMGA agent for collective market governance
 */

export interface FPO {
  id: string;
  name: string;
  village: string;
  district: string;
  state: string;
  total_members: number;
  total_land_area: number;
  status: string;
  contact_person: string;
  contact_phone: string;
  created_at: string;
}

export interface FPOMember {
  id: string;
  fpo_id: string;
  user_id: string;
  join_date: string;
  land_area: number;
  role: string;
  investment_units: number;
  status: string;
}

export interface CollectivePortfolio {
  id: string;
  fpo_id: string;
  season: string;
  year: number;
  planned_crops: any;
  risk_score: number;
  expected_revenue: number;
  diversification_index: number;
  sharpe_ratio: number;
  status: string;
}

export interface ProfitDistribution {
  id: string;
  fpo_id: string;
  member_id: string;
  investment_units: number;
  share_percentage: number;
  gross_profit: number;
  deductions: number;
  net_profit: number;
  payment_status: string;
}

/**
 * Fetch FPO details
 */
export const useFPO = (fpoId: string) => {
  return useQuery({
    queryKey: ['fpo', fpoId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('fpos')
        .select('*')
        .eq('id', fpoId)
        .single();

      if (error) throw error;
      return data as FPO;
    },
    enabled: !!fpoId
  });
};

/**
 * Fetch all FPOs (for listing)
 */
export const useFPOs = () => {
  return useQuery({
    queryKey: ['fpos'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('fpos')
        .select('*')
        .eq('status', 'active')
        .order('name');

      if (error) throw error;
      return data as FPO[];
    }
  });
};

/**
 * Fetch FPO members
 */
export const useFPOMembers = (fpoId: string) => {
  return useQuery({
    queryKey: ['fpo-members', fpoId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('fpo_members')
        .select(`
          *,
          users (
            id,
            email
          )
        `)
        .eq('fpo_id', fpoId)
        .eq('status', 'active');

      if (error) throw error;
      return data as FPOMember[];
    },
    enabled: !!fpoId
  });
};

/**
 * Fetch collective portfolio
 */
export const useCollectivePortfolio = (fpoId: string, season?: string) => {
  return useQuery({
    queryKey: ['collective-portfolio', fpoId, season],
    queryFn: async () => {
      let query = supabase
        .from('collective_portfolios')
        .select('*')
        .eq('fpo_id', fpoId);

      if (season) {
        query = query.eq('season', season);
      }

      const { data, error } = await query
        .order('created_at', { ascending: false })
        .limit(1)
        .single();

      if (error && error.code !== 'PGRST116') throw error; // Ignore "no rows" error
      return data as CollectivePortfolio | null;
    },
    enabled: !!fpoId
  });
};

/**
 * Fetch profit distributions
 */
export const useProfitDistributions = (fpoId: string, portfolioId?: string) => {
  return useQuery({
    queryKey: ['profit-distributions', fpoId, portfolioId],
    queryFn: async () => {
      let query = supabase
        .from('profit_distributions')
        .select(`
          *,
          fpo_members (
            user_id,
            land_area,
            users (
              email
            )
          )
        `)
        .eq('fpo_id', fpoId);

      if (portfolioId) {
        query = query.eq('portfolio_id', portfolioId);
      }

      const { data, error } = await query.order('net_profit', { ascending: false });

      if (error) throw error;
      return data as ProfitDistribution[];
    },
    enabled: !!fpoId
  });
};

/**
 * Create new collective portfolio (calls CMGA agent)
 */
export const useCreatePortfolio = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (portfolioData: {
      fpoId: string;
      season: string;
      year: number;
      constraints: any;
      cropOptions: any[];
    }) => {
      // TODO: Call CMGA agent via MCP
      // For now, insert directly to database
      const { data, error } = await supabase
        .from('collective_portfolios')
        .insert({
          fpo_id: portfolioData.fpoId,
          season: portfolioData.season,
          year: portfolioData.year,
          planned_crops: portfolioData.cropOptions,
          status: 'planning'
        })
        .select()
        .single();

      if (error) throw error;
      return data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['collective-portfolio', variables.fpoId] });
    }
  });
};

/**
 * Calculate investment units for a member (calls CMGA agent)
 */
export const useCalculateInvestmentUnits = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      fpoId: string;
      memberId: string;
      factors: {
        landArea: number;
        soilQuality: number;
        inputsValue: number;
        laborDays: number;
        waterAccess: number;
        equipmentContribution: number;
      };
    }) => {
      // TODO: Call CMGA agent via MCP
      // For now, simple calculation
      const units =
        data.factors.landArea * 40 +
        data.factors.soilQuality * 10 +
        (data.factors.inputsValue / 1000) * 20 +
        data.factors.laborDays * 0.15 +
        data.factors.waterAccess * 10 +
        (data.factors.equipmentContribution / 1000) * 5;

      // Update in database
      const { error } = await supabase
        .from('fpo_members')
        .update({ investment_units: units })
        .eq('id', data.memberId);

      if (error) throw error;

      return { units, memberId: data.memberId };
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['fpo-members', variables.fpoId] });
    }
  });
};

/**
 * Distribute profits (calls CMGA agent)
 */
export const useDistributeProfits = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      fpoId: string;
      portfolioId: string;
      totalRevenue: number;
      costs: number;
    }) => {
      // TODO: Call CMGA agent via MCP
      // For now, return mock data
      return {
        success: true,
        totalProfit: data.totalRevenue - data.costs,
        distributions: []
      };
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['profit-distributions', variables.fpoId] });
    }
  });
};

/**
 * Get FPO insights (calls CMGA agent)
 */
export const useFPOInsights = (fpoId: string) => {
  return useQuery({
    queryKey: ['fpo-insights', fpoId],
    queryFn: async () => {
      // TODO: Call CMGA agent via MCP
      // For now, return mock insights
      return {
        performanceScore: 75,
        riskLevel: 'medium',
        recommendations: [
          'Consider adding more drought-resistant crops',
          'Increase crop diversification',
          'Recruit 5 more members to reach optimal size'
        ]
      };
    },
    enabled: !!fpoId
  });
};
