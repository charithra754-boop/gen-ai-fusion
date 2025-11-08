import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { DollarSign, TrendingUp, Users } from 'lucide-react';
import type { ProfitDistribution, CollectivePortfolio } from '@/hooks/useFPOData';

interface ProfitDistributionViewProps {
  distributions: ProfitDistribution[];
  portfolio: CollectivePortfolio | null;
  fpoId: string;
}

export function ProfitDistributionView({
  distributions,
  portfolio
}: ProfitDistributionViewProps) {
  if (distributions.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-12">
            <DollarSign className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Distributions Yet</h3>
            <p className="text-muted-foreground mb-4">
              Profit distributions will appear here after harvest and sale.
            </p>
            {portfolio && portfolio.status === 'active' && (
              <Button>Record Harvest & Sales</Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  const totalProfit = distributions.reduce((sum, d) => sum + d.net_profit, 0);
  const paidCount = distributions.filter(d => d.payment_status === 'paid').length;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <DollarSign className="w-4 h-4" />
              Total Distributed
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">₹{(totalProfit / 100000).toFixed(2)}L</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <Users className="w-4 h-4" />
              Members
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{distributions.length}</p>
            <p className="text-xs text-muted-foreground mt-1">{paidCount} paid</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Average Share
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">
              ₹{(totalProfit / distributions.length / 1000).toFixed(1)}K
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Distribution Table */}
      <Card>
        <CardHeader>
          <CardTitle>Profit Distribution Breakdown</CardTitle>
          <CardDescription>Based on Investment Units</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {distributions.map((dist, idx) => (
              <div
                key={dist.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-sm font-semibold">#{idx + 1}</span>
                  </div>
                  <div>
                    <p className="font-medium">{dist.member_id}</p>
                    <p className="text-xs text-muted-foreground">
                      {dist.investment_units.toFixed(2)} units •{' '}
                      {dist.share_percentage.toFixed(2)}%
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <p className="text-lg font-bold text-green-600">
                    ₹{dist.net_profit.toLocaleString('en-IN')}
                  </p>
                  {dist.deductions > 0 && (
                    <p className="text-xs text-muted-foreground">
                      (₹{dist.deductions.toLocaleString('en-IN')} deducted)
                    </p>
                  )}
                  <Badge
                    variant={dist.payment_status === 'paid' ? 'default' : 'secondary'}
                    className="mt-1"
                  >
                    {dist.payment_status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
