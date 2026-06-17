"use client";

import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Heading,
} from "@chakra-ui/react";

interface TraceStep {
  agent: string;
  summary: string;
  confidence: number;
  reasoning: string;
  assumptions: string[];
  missing_data: string[];
}

const agentLabels: Record<string, string> = {
  resume_agent: "Resume Intelligence Agent",
  role_research_agent: "Role Research Agent",
  skill_gap_agent: "Skill Gap Analysis Agent",
  career_twin_agent: "Career Twin Agent",
  strategy_agent: "Career Strategy Agent",
  roadmap_agent: "Roadmap Agent",
  project_agent: "Project Agent",
  interview_agent: "Interview Coach",
  readiness_agent: "Readiness Agent",
};

export default function AgentTraceViewer({
  trace,
}: {
  trace: TraceStep[];
}) {
  return (
    <Box bg="white" borderRadius="2xl" p={6} shadow="md">
      <Heading size="md" mb={5}>
        Multi-Agent Reasoning Trace
      </Heading>

      <VStack align="stretch" spacing={4}>
        {trace?.map((step, index) => (
          <Box
            key={index}
            borderWidth="1px"
            borderRadius="lg"
            p={4}
          >
            <HStack justify="space-between" mb={2}>
              <Text fontWeight="bold">
                {agentLabels[step.agent] || step.agent}
              </Text>

              <Badge colorScheme="blue">
                {Math.round((step.confidence || 0) * 100)}%
              </Badge>
            </HStack>

            <Text fontSize="sm" mb={2}>
              {step.summary}
            </Text>

            {step.reasoning && (
              <Text
                fontSize="sm"
                color="gray.600"
                mb={2}
              >
                {step.reasoning}
              </Text>
            )}

            {step.assumptions?.length > 0 && (
              <Box mt={2}>
                <Text
                  fontSize="xs"
                  fontWeight="bold"
                  mb={1}
                >
                  Assumptions
                </Text>

                {step.assumptions.map((a, i) => (
                  <Badge
                    key={i}
                    mr={1}
                    mb={1}
                    colorScheme="orange"
                  >
                    {a}
                  </Badge>
                ))}
              </Box>
            )}

            {step.missing_data?.length > 0 && (
              <Box mt={2}>
                <Text
                  fontSize="xs"
                  fontWeight="bold"
                  mb={1}
                >
                  Missing Data
                </Text>

                {step.missing_data.map((m, i) => (
                  <Badge
                    key={i}
                    mr={1}
                    mb={1}
                    colorScheme="red"
                  >
                    {m}
                  </Badge>
                ))}
              </Box>
            )}
          </Box>
        ))}
      </VStack>
    </Box>
  );
}