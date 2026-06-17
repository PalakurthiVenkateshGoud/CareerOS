"use client";
import {
  Box,
  Heading,
  VStack,
  HStack,
  Text,
  Badge,
  SimpleGrid,
} from "@chakra-ui/react";
interface CareerTwinProps {
  data: any;
  targetRole?: string;
}
export default function CareerTwin({
  data,
  targetRole,
}: CareerTwinProps) {
  const current = data?.current_you?.[0];
  const future = data?.future_you?.[0];
  return (
    <Box bg="white" borderRadius="2xl" p={6} shadow="md">
      <Heading size="md" mb={5}>
        Career Twin
      </Heading>
      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
        <Box>
          <Text fontWeight="bold" mb={2}>
            Current You
          </Text>
          <Badge colorScheme="gray" mb={2}>
            {current?.title || "Current"}
          </Badge>
          <Text fontSize="sm">
            {current?.description}
          </Text>
        </Box>
        <Box>
          <Text fontWeight="bold" mb={2}>
            Future You {targetRole ? `(${targetRole})` : ""}
          </Text>
          <Badge colorScheme="blue" mb={2}>
            {future?.title || "Future"}
          </Badge>
          <Text fontSize="sm">
            {future?.description}
          </Text>
        </Box>
      </SimpleGrid>
      <VStack align="stretch" mt={6} spacing={3}>
        <Text fontWeight="bold">
          Transformation Highlights
        </Text>
        {data?.transformation_highlights?.map(
          (item: any, index: number) => (
            <Box
              key={index}
              borderWidth="1px"
              borderRadius="md"
              p={3}
            >
              <HStack justify="space-between">
                <Text fontWeight="semibold">
                  {item.skill}
                </Text>
                <Badge colorScheme="green">
                  {item.status}
                </Badge>
              </HStack>
              <Text fontSize="sm" mt={1}>
                {item.description}
              </Text>
              <Text
                fontSize="xs"
                color="gray.500"
                mt={1}
              >
                Importance: {item.importance}/10
              </Text>
            </Box>
          )
        )}
      </VStack>
    </Box>
  );
}