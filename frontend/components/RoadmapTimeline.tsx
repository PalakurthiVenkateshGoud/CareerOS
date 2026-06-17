"use client";

import {
  Box,
  Heading,
  VStack,
  HStack,
  Text,
  Badge,
} from "@chakra-ui/react";

interface RoadmapTask {
  title: string;
  resource_type: string;
  hours: number;
  skill_gap?: string;
}

interface RoadmapPeriod {
  period: string;
  focus_skills: string[];
  tasks: RoadmapTask[];
}

interface RoadmapData {
  timeline: RoadmapPeriod[];
  estimated_completion_weeks: number;
}

export default function RoadmapTimeline({
  data,
}: {
  data: RoadmapData;
}) {
  return (
    <Box bg="white" borderRadius="2xl" p={6} shadow="md">
      <HStack justify="space-between" mb={4}>
        <Heading size="md">
          Learning Roadmap
        </Heading>

        <Badge colorScheme="blue" px={3} py={1}>
          ~{data.estimated_completion_weeks} Weeks
        </Badge>
      </HStack>

      <VStack align="stretch" spacing={5}>
        {data.timeline?.map((period, i) => (
          <Box
            key={i}
            borderLeft="4px solid"
            borderColor="blue.500"
            pl={4}
          >
            <Text
              fontWeight="bold"
              fontSize="lg"
              mb={2}
            >
              {period.period}
            </Text>

            <HStack wrap="wrap" spacing={2} mb={3}>
              {period.focus_skills?.map((skill) => (
                <Badge
                  key={skill}
                  colorScheme="purple"
                >
                  {skill}
                </Badge>
              ))}
            </HStack>

            <VStack align="stretch" spacing={3}>
              {period.tasks?.map((task, j) => (
                <Box
                  key={j}
                  bg="gray.50"
                  borderRadius="md"
                  p={3}
                >
                  <HStack justify="space-between">
                    <Text fontWeight="semibold">
                      {task.title}
                    </Text>

                    <HStack>
                      <Badge colorScheme="gray">
                        {task.resource_type}
                      </Badge>

                      <Badge colorScheme="blue">
                        {task.hours}H
                      </Badge>
                    </HStack>
                  </HStack>

                  {task.skill_gap && (
                    <Text
                      mt={2}
                      fontSize="xs"
                      color="gray.500"
                    >
                      Skill Gap: {task.skill_gap}
                    </Text>
                  )}
                </Box>
              ))}
            </VStack>
          </Box>
        ))}
      </VStack>
    </Box>
  );
}