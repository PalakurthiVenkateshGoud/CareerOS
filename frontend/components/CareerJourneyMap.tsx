"use client";
import { Box, HStack, VStack, Text, Circle, Divider } from "@chakra-ui/react";

const STAGES = [
  { key: "current", label: "Current State" },
  { key: "gaps", label: "Skill Gaps" },
  { key: "roadmap", label: "Roadmap" },
  { key: "projects", label: "Projects" },
  { key: "interview", label: "Interview Ready" },
  { key: "target", label: "Target Role" },
];

export default function CareerJourneyMap({
  activeStage = "target",
}: {
  activeStage?: string;
}) {
  const activeIndex = STAGES.findIndex((s) => s.key === activeStage);

  return (
    <Box bg="white" borderRadius="2xl" p={6} shadow="md" overflowX="auto">
      <Text fontWeight="bold" mb={4}>
        Your Career Journey
      </Text>
      <HStack spacing={0} minW="700px">
        {STAGES.map((stage, i) => (
          <HStack key={stage.key} flex={1} spacing={0}>
            <VStack spacing={2} flex="0 0 auto">
              <Circle
                size="40px"
                bg={i <= activeIndex ? "gray.800" : "gray.200"}
                color={i <= activeIndex ? "white" : "gray.500"}
                fontWeight="bold"
              >
                {i + 1}
              </Circle>
              <Text
                fontSize="xs"
                textAlign="center"
                maxW="80px"
                fontWeight={i === activeIndex ? "bold" : "normal"}
              >
                {stage.label}
              </Text>
            </VStack>
            {i < STAGES.length - 1 && (
              <Divider
                flex={1}
                borderWidth="2px"
                borderColor={i < activeIndex ? "gray.800" : "gray.200"}
                orientation="horizontal"
              />
            )}
          </HStack>
        ))}
      </HStack>
    </Box>
  );
}