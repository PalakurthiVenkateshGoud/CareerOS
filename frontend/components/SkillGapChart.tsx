"use client";
import {
  Box,
  Heading,
  VStack,
  HStack,
  Text,
  Badge,
} from "@chakra-ui/react";
export default function SkillGapChart({ data }: { data: any }) {
  return (
    <Box bg="white" borderRadius="2xl" p={6} shadow="md">
      <Heading size="md" mb={4}>
        Skill Gap Analysis
      </Heading>
      <Text fontWeight="bold" mb={2}>
        Matched Skills
      </Text>
      <HStack wrap="wrap" spacing={2} mb={6}>
        {data?.strengths?.map((skill: string) => (
          <Badge key={skill} colorScheme="green" px={3} py={1}>
            {skill}
          </Badge>
        ))}
      </HStack>
      <Text fontWeight="bold" mb={2}>
        Missing Skills
      </Text>
      <HStack wrap="wrap" spacing={2} mb={6}>
        {data?.missing_skills?.map((skill: string) => (
          <Badge key={skill} colorScheme="red" px={3} py={1}>
            {skill}
          </Badge>
        ))}
      </HStack>
      <Text fontWeight="bold" mb={3}>
        Priority Gaps
      </Text>
      <VStack align="stretch" spacing={3}>
        {data?.priority_gaps?.map((gap: any, i: number) => (
          <Box
            key={i}
            borderWidth="1px"
            borderRadius="lg"
            p={4}
          >
            <HStack justify="space-between" mb={2}>
              <Text fontWeight="bold">
                {gap.skill}
              </Text>
              <Badge colorScheme="orange">
                Importance {gap.importance}/10
              </Badge>
            </HStack>
            <Text fontSize="sm" color="gray.600">
              {gap.description}
            </Text>
          </Box>
        ))}
      </VStack>
    </Box>
  );
}