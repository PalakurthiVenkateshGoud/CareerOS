"use client";

import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  VStack,
  SimpleGrid,
  Icon,
  HStack,
} from "@chakra-ui/react";
import { useRouter } from "next/navigation";
import { Brain, Target, Map, Briefcase, MessageSquare, Sparkles } from "lucide-react";
import CareerJourneyMap from "@/components/CareerJourneyMap";

const FEATURES = [
  { icon: Target, title: "Role Research", desc: "Understands what your target role actually requires." },
  { icon: Brain, title: "Skill Gap Analysis", desc: "Pinpoints exactly what's missing from your profile." },
  { icon: Sparkles, title: "Career Twin", desc: "See who you are now vs. who you'll become." },
  { icon: Map, title: "Learning Roadmap", desc: "A week-by-week plan tailored to your time." },
  { icon: Briefcase, title: "Project Recommendations", desc: "Portfolio projects ranked by impact." },
  { icon: MessageSquare, title: "Interview Prep", desc: "HR, technical, and project-based questions." },
];

export default function LandingPage() {
  const router = useRouter();

  return (
    <Box bg="gray.50" minH="100vh">
      <Container maxW="5xl" py={16} color="gray.800">
        <VStack spacing={6} textAlign="center">
          <HStack
            bg="indigo.50"
            color="indigo.700"
            px={4}
            py={1}
            borderRadius="full"
            fontSize="sm"
            fontWeight="semibold"
          >
            <Icon as={Sparkles} boxSize={4} />
            <Text>Multi-Agent Career Intelligence Platform</Text>
          </HStack>

          <Heading size="2xl" color="gray.800">CareerOS</Heading>

          <Text fontSize="xl" color="gray.600" maxW="2xl">
            Your AI-Powered Multi-Agent Career Intelligence Platform — from
            resume to readiness, powered by transparent agent reasoning.
          </Text>

          <Button
  size="lg"
  bg="gray.900"
  color="white"
  _hover={{ bg: "gray.700" }}
  onClick={() => router.push("/upload")}
>
  Get Started — Analyze My Career
</Button>
        </VStack>

        <Box mt={16}>
          <CareerJourneyMap activeStage="target" />
        </Box>

        <SimpleGrid columns={{ base: 1, md: 3 }} gap={6} mt={16}>
          {FEATURES.map((f, i) => (
            <Box
              key={i}
              bg="white"
              borderRadius="xl"
              p={6}
              shadow="md"
              border="1px solid"
              borderColor="gray.200"
              color="gray.800"
            >
              <Icon as={f.icon} boxSize={6} color="indigo.500" mb={3} />
              <Heading size="sm" mb={2} color="gray.800">
                {f.title}
              </Heading>
              <Text fontSize="sm" color="gray.600">
                {f.desc}
              </Text>
            </Box>
          ))}
        </SimpleGrid>
      </Container>
    </Box>
  );
}