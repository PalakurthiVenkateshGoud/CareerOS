"use client";
import {
  Box,
  Heading,
  Text,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  VStack,
} from "@chakra-ui/react";
import {
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
  ResponsiveContainer,
} from "recharts";

interface ReadinessData {
  current_readiness: number;
  projection: {
    "3_months": number;
    "6_months": number;
    "12_months": number;
  };
  methodology: string;
  key_levers: { action: string; why: string }[];
}

export default function ReadinessGauge({ data }: { data: ReadinessData }) {
  const chartData = [
    { name: "readiness", value: data.current_readiness, fill: "#4F46E5" },
  ];

  return (
    <Box bg="white" borderRadius="2xl" p={6} shadow="md">
      <Heading size="md" mb={4}>
        Career Readiness Score
      </Heading>

      <ResponsiveContainer width="100%" height={200}>
        <RadialBarChart
          innerRadius="70%"
          outerRadius="100%"
          data={chartData}
          startAngle={90}
          endAngle={-270}
        >
          <PolarAngleAxis
            type="number"
            domain={[0, 100]}
            angleAxisId={0}
            tick={false}
          />
          <RadialBar background dataKey="value" cornerRadius={10} />
        </RadialBarChart>
      </ResponsiveContainer>

      <Text textAlign="center" fontSize="2xl" fontWeight="bold">
        {data.current_readiness}%
      </Text>

      <SimpleGrid columns={3} mt={4} gap={2}>
        <Stat>
          <StatLabel>3 Months</StatLabel>
          <StatNumber>{data.projection["3_months"]}%</StatNumber>
        </Stat>
        <Stat>
          <StatLabel>6 Months</StatLabel>
          <StatNumber>{data.projection["6_months"]}%</StatNumber>
        </Stat>
        <Stat>
          <StatLabel>12 Months</StatLabel>
          <StatNumber>{data.projection["12_months"]}%</StatNumber>
        </Stat>
      </SimpleGrid>

      <Text mt={4} fontSize="sm" color="gray.600">
        {data.methodology}
      </Text>

      {data.key_levers?.length > 0 && (
        <VStack align="stretch" mt={4} spacing={2}>
          <Text fontWeight="bold" fontSize="sm">
            Key Levers to Improve Your Score
          </Text>
          {data.key_levers.map((lever, i) => (
            <Box key={i} bg="indigo.50" borderRadius="md" px={3} py={2}>
              <Text fontSize="sm" fontWeight="semibold">
                {lever.action}
              </Text>
              <Text fontSize="xs" color="gray.600">
                {lever.why}
              </Text>
            </Box>
          ))}
        </VStack>
      )}
    </Box>
  );
}