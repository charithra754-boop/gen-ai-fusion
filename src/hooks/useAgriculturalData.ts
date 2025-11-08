
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { supabase } from '@/integrations/supabase/client';

export const useCropRecommendations = (region?: string, season?: string) => {
  return useQuery({
    queryKey: ['crop-recommendations', region, season],
    queryFn: async () => {
      let query = supabase.from('crop_recommendations').select('*');
      
      if (region) {
        query = query.eq('region', region);
      }
      if (season) {
        query = query.eq('season', season);
      }
      
      const { data, error } = await query.order('profitability_score', { ascending: false });
      
      if (error) throw error;
      return data;
    }
  });
};

export const useWeatherData = (location?: string) => {
  return useQuery({
    queryKey: ['weather-data', location],
    queryFn: async () => {
      let query = supabase.from('weather_data').select('*');
      
      if (location) {
        query = query.eq('location', location);
      }
      
      const { data, error } = await query.order('date', { ascending: false }).limit(7);
      
      if (error) throw error;
      return data;
    }
  });
};

export const useFarmingTips = (category?: string, language?: string) => {
  return useQuery({
    queryKey: ['farming-tips', category, language],
    queryFn: async () => {
      let query = supabase.from('farming_tips').select('*');
      
      if (category) {
        query = query.eq('category', category);
      }
      
      const { data, error } = await query.order('priority', { ascending: false });
      
      if (error) throw error;
      return data;
    }
  });
};

export const useSoilAnalysis = () => {
  const queryClient = useQueryClient();

  const predictCrop = useMutation({
    mutationFn: async (soilData: {
      nitrogen: number;
      phosphorus: number;
      potassium: number;
      temperature: number;
      humidity: number;
      ph: number;
      rainfall: number;
      location?: string;
    }) => {
      // Call the edge function for ML prediction
      const { data: prediction, error: predictionError } = await supabase.functions.invoke('predict-crop', {
        body: soilData
      });

      if (predictionError) {
        console.error('Prediction error:', predictionError);
        // Fallback: save data without prediction
        const { data, error } = await supabase
          .from('soil_analysis')
          .insert([soilData])
          .select()
          .single();
        
        if (error) throw error;
        return { ...data, predicted_crop: 'Analysis pending', confidence_score: null };
      }

      // Save the analysis with prediction to database
      const analysisData = {
        ...soilData,
        predicted_crop: prediction.predicted_crop,
        confidence_score: prediction.confidence_score,
        alternative_crops: prediction.alternative_crops
      };

      const { data, error } = await supabase
        .from('soil_analysis')
        .insert([analysisData])
        .select()
        .single();
      
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['soil-analysis'] });
    }
  });

  const getSoilAnalysisHistory = useQuery({
    queryKey: ['soil-analysis'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('soil_analysis')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(10);
      
      if (error) throw error;
      return data;
    }
  });

  return { predictCrop, getSoilAnalysisHistory };
};

export const useAIConversations = () => {
  const queryClient = useQueryClient();

  const saveConversation = useMutation({
    mutationFn: async (conversation: {
      user_query: string;
      user_query_kannada?: string;
      ai_response: string;
      ai_response_kannada?: string;
      language: string;
      location?: string;
    }) => {
      const { data, error } = await supabase
        .from('ai_conversations')
        .insert([conversation])
        .select()
        .single();
      
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-conversations'] });
    }
  });

  return { saveConversation };
};
