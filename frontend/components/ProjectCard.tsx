"use client";
import {
  Box,
  Heading,
  SimpleGrid,
  VStack,
  HStack,
  Text,
  Badge,
} from "@chakra-ui/react";
import ExplanationCallout from "./ExplanationCallout";

interface Project {
  title: string;
  description: string;
  skills_demonstrated: string[];
  difficulty: string;
  estimated_hours: number;
  relevance_explanation: string;
  impact_rank: number;
}

const difficultyColor = {
  easy: "green",
  medium: "orange",
  hard: "red",
};
export default function ProjectCard({ projects }: { projects: Project[] }) {
  const sorted = [...(projects || [])].sort(
    (a, b) => (a.impact_rank || 0) - (b.impact_rank || 0)
  );

  return (
    <Box bg="white" borderRadius="2xl" p={6} shadow="md">
      <Heading size="md" mb={4}>
        Recommended Projects
      </Heading>

      <SimpleGrid columns={{ base: 1, md: 2 }} gap={4}>
        {sorted.map((project, i) => (
          <Box key={i} borderWidth="1px" borderRadius="lg" p={4}>
            <HStack justify="space-between" mb={2}>
              <Text fontWeight="bold">{project.title}</Text>
              <Badge
                colorScheme={
                  difficultyColor[project.difficulty?.toLowerCase()] || "gray"
                }
              >
                {project.difficulty}
              </Badge>
            </HStack>

            <Text fontSize="sm" color="gray.600" mb={2}>
              {project.description}
            </Text>

            <HStack wrap="wrap" spacing={2} mb={2}>
              {project.skills_demonstrated?.map((skill) => (
                <Badge key={skill} colorScheme="indigo" px={2} py={1}>
                  {skill}
                </Badge>
              ))}
            </HStack>

            <Text fontSize="xs" color="gray.500">
              Estimated effort: {project.estimated_hours}h
            </Text>

            <ExplanationCallout text={project.relevance_explanation} />
          </Box>
        ))}
      </SimpleGrid>
    </Box>
  );
}