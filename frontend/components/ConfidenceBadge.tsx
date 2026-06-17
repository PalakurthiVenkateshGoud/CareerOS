"use client";
import { Badge } from "@chakra-ui/react";

export default function ConfidenceBadge({ confidence }: { confidence: number }) {
  const pct = Math.round(confidence * 100);
  const colorScheme = pct >= 75 ? "green" : pct >= 50 ? "yellow" : "red";

  return (
    <Badge colorScheme={colorScheme} px={2} py={1}>
      {pct}% confidence
    </Badge>
  );
}