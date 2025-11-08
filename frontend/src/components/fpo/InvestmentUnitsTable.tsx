import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Calculator, TrendingUp } from 'lucide-react';
import type { FPOMember } from '@/hooks/useFPOData';

interface InvestmentUnitsTableProps {
  members: FPOMember[];
  fpoId: string;
  loading: boolean;
}

export function InvestmentUnitsTable({ members, fpoId, loading }: InvestmentUnitsTableProps) {
  if (loading) {
    return <Skeleton className="h-96" />;
  }

  const sortedMembers = [...members].sort(
    (a, b) => (b.investment_units || 0) - (a.investment_units || 0)
  );

  const totalUnits = members.reduce((sum, m) => sum + (m.investment_units || 0), 0);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Investment Units Ledger</CardTitle>
            <CardDescription>
              Transparent tracking of member contributions
            </CardDescription>
          </div>
          <div className="text-right">
            <p className="text-sm text-muted-foreground">Total Units</p>
            <p className="text-2xl font-bold">{totalUnits.toFixed(2)}</p>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {members.length === 0 ? (
          <div className="text-center py-12">
            <Calculator className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Investment Units Calculated</h3>
            <p className="text-muted-foreground mb-4">
              Calculate investment units for members to enable fair profit distribution.
            </p>
            <Button>Calculate Units</Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Rank</TableHead>
                    <TableHead>Member</TableHead>
                    <TableHead>Land Area</TableHead>
                    <TableHead>Investment Units</TableHead>
                    <TableHead className="text-right">Share %</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sortedMembers.map((member, idx) => {
                    const sharePercentage =
                      totalUnits > 0 ? ((member.investment_units || 0) / totalUnits) * 100 : 0;

                    return (
                      <TableRow key={member.id}>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <span className="text-muted-foreground">#{idx + 1}</span>
                            {idx === 0 && (
                              <Badge variant="default" className="text-xs">
                                <TrendingUp className="w-3 h-3 mr-1" />
                                Top
                              </Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div>
                            <p className="font-medium">{member.user_id}</p>
                            <p className="text-xs text-muted-foreground capitalize">
                              {member.role}
                            </p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <span className="text-sm">{member.land_area} ha</span>
                        </TableCell>
                        <TableCell>
                          <div>
                            <p className="font-medium">{(member.investment_units || 0).toFixed(2)}</p>
                            <p className="text-xs text-muted-foreground">units</p>
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                          <div>
                            <p className="font-semibold">{sharePercentage.toFixed(2)}%</p>
                            <div className="w-20 ml-auto mt-1">
                              <div className="h-2 bg-muted rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-primary"
                                  style={{ width: `${sharePercentage}%` }}
                                />
                              </div>
                            </div>
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>

            <div className="bg-muted/50 rounded-lg p-4">
              <h4 className="font-semibold mb-2 text-sm">How Investment Units Work</h4>
              <p className="text-xs text-muted-foreground">
                Investment Units are calculated based on: <strong>Land</strong> (40%),{' '}
                <strong>Inputs</strong> (20%), <strong>Labor</strong> (15%),{' '}
                <strong>Soil Quality</strong> (10%), <strong>Water Access</strong> (10%), and{' '}
                <strong>Equipment</strong> (5%). Higher units mean higher profit share.
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
