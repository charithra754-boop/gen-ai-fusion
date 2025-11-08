export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  public: {
    Tables: {
      ai_conversations: {
        Row: {
          ai_response: string
          ai_response_kannada: string | null
          created_at: string
          id: string
          language: string | null
          location: string | null
          user_query: string
          user_query_kannada: string | null
        }
        Insert: {
          ai_response: string
          ai_response_kannada?: string | null
          created_at?: string
          id?: string
          language?: string | null
          location?: string | null
          user_query: string
          user_query_kannada?: string | null
        }
        Update: {
          ai_response?: string
          ai_response_kannada?: string | null
          created_at?: string
          id?: string
          language?: string | null
          location?: string | null
          user_query?: string
          user_query_kannada?: string | null
        }
        Relationships: []
      }
      crop_recommendations: {
        Row: {
          created_at: string
          crop_name: string
          growing_duration: number | null
          id: string
          profitability_score: number | null
          rainfall_required: number | null
          region: string | null
          season: string
          soil_type: string | null
          temperature_max: number | null
          temperature_min: number | null
          updated_at: string
        }
        Insert: {
          created_at?: string
          crop_name: string
          growing_duration?: number | null
          id?: string
          profitability_score?: number | null
          rainfall_required?: number | null
          region?: string | null
          season: string
          soil_type?: string | null
          temperature_max?: number | null
          temperature_min?: number | null
          updated_at?: string
        }
        Update: {
          created_at?: string
          crop_name?: string
          growing_duration?: number | null
          id?: string
          profitability_score?: number | null
          rainfall_required?: number | null
          region?: string | null
          season?: string
          soil_type?: string | null
          temperature_max?: number | null
          temperature_min?: number | null
          updated_at?: string
        }
        Relationships: []
      }
      farming_tips: {
        Row: {
          category: string
          created_at: string
          crop_type: string | null
          id: string
          priority: number | null
          season: string | null
          tip_content: string
          tip_content_kannada: string | null
          tip_title: string
          tip_title_kannada: string | null
        }
        Insert: {
          category: string
          created_at?: string
          crop_type?: string | null
          id?: string
          priority?: number | null
          season?: string | null
          tip_content: string
          tip_content_kannada?: string | null
          tip_title: string
          tip_title_kannada?: string | null
        }
        Update: {
          category?: string
          created_at?: string
          crop_type?: string | null
          id?: string
          priority?: number | null
          season?: string | null
          tip_content?: string
          tip_content_kannada?: string | null
          tip_title?: string
          tip_title_kannada?: string | null
        }
        Relationships: []
      }
      soil_analysis: {
        Row: {
          alternative_crops: Json | null
          confidence_score: number | null
          created_at: string
          humidity: number
          id: string
          location: string | null
          nitrogen: number
          ph: number
          phosphorus: number
          potassium: number
          predicted_crop: string | null
          rainfall: number
          temperature: number
          user_feedback: string | null
        }
        Insert: {
          alternative_crops?: Json | null
          confidence_score?: number | null
          created_at?: string
          humidity: number
          id?: string
          location?: string | null
          nitrogen: number
          ph: number
          phosphorus: number
          potassium: number
          predicted_crop?: string | null
          rainfall: number
          temperature: number
          user_feedback?: string | null
        }
        Update: {
          alternative_crops?: Json | null
          confidence_score?: number | null
          created_at?: string
          humidity?: number
          id?: string
          location?: string | null
          nitrogen?: number
          ph?: number
          phosphorus?: number
          potassium?: number
          predicted_crop?: string | null
          rainfall?: number
          temperature?: number
          user_feedback?: string | null
        }
        Relationships: []
      }
      weather_data: {
        Row: {
          created_at: string
          date: string
          humidity: number | null
          id: string
          location: string
          rainfall: number | null
          temperature: number | null
          weather_condition: string | null
          wind_speed: number | null
        }
        Insert: {
          created_at?: string
          date: string
          humidity?: number | null
          id?: string
          location: string
          rainfall?: number | null
          temperature?: number | null
          weather_condition?: string | null
          wind_speed?: number | null
        }
        Update: {
          created_at?: string
          date?: string
          humidity?: number | null
          id?: string
          location?: string
          rainfall?: number | null
          temperature?: number | null
          weather_condition?: string | null
          wind_speed?: number | null
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DefaultSchema = Database[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof (Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        Database[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? (Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      Database[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof Database },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof Database },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends { schema: keyof Database }
  ? Database[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
