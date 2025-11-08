// backend/functions/get-crop-recommendations/index.ts
import { createClient } from '@supabase/supabase-js';
import { corsHeaders } from '../_shared/cors.ts';

const supabase = createClient(
  Deno.env.get('SUPABASE_URL') ?? '',
  Deno.env.get('SUPABASE_ANON_KEY') ?? ''
);

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const { nitrogen, phosphorus, potassium, ph } = await req.json();

    const { data, error } = await supabase
      .from('crop_recommendations')
      .select('*, crops(*)')
      .gte('min_n', nitrogen)
      .lte('max_n', nitrogen)
      .gte('min_p', phosphorus)
      .lte('max_p', phosphorus)
      .gte('min_k', potassium)
      .lte('max_k', potassium)
      .gte('min_ph', ph)
      .lte('max_ph', ph);

    if (error) {
      throw error;
    }

    if (data.length > 0) {
      const bestCrop = data[0];
      const alternativeCrops = data.slice(1).map((c: any) => c.crops.name);

      return new Response(JSON.stringify({
        predicted_crop: bestCrop.crops.name,
        confidence_score: 95, // Dummy score
        alternative_crops: alternativeCrops,
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      });
    } else {
      return new Response(JSON.stringify({
        predicted_crop: 'No suitable crop found',
        confidence_score: 0,
        alternative_crops: [],
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      });
    }
  } catch (err) {
    return new Response(String(err?.message ?? err), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 500,
    });
  }
});
