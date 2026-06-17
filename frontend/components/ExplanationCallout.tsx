import { Box, Text } from "@chakra-ui/react";

export default function ExplanationCallout({ text }: { text: string }) {
  if (!text) return null;

  return (
    <Box bg="indigo.50" borderRadius="md" px={3} py={2} mt={2}>
      <Text fontSize="xs" color="indigo.700">
        <Text as="span" fontWeight="bold">
          Why CareerOS recommends this:{" "}
        </Text>
        {text}
      </Text>
    </Box>
  );
}