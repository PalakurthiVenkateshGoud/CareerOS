"use client";

import {
  Container,
  Heading,
  Text,
  VStack,
  Button,
  Input,
  FormControl,
  FormLabel,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  useToast,
} from "@chakra-ui/react";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { analyzeCareer } from "@/lib/api";

export default function ConfigurePage() {
  const router = useRouter();
  const toast = useToast();

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [targetRole, setTargetRole] = useState("");
  const [hoursPerWeek, setHoursPerWeek] = useState(10);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const sid = sessionStorage.getItem("session_id");

    if (!sid) {
      toast({
        title: "No resume found",
        description: "Please upload your resume first.",
        status: "warning",
      });

      router.push("/upload");
      return;
    }

    setSessionId(sid);
  }, [router, toast]);

  const handleAnalyze = async () => {
    if (!sessionId || !targetRole.trim()) {
      toast({
        title: "Target role required",
        description: "Please enter the role you're aiming for.",
        status: "error",
      });
      return;
    }

    setLoading(true);

    try {
      const result = await analyzeCareer(
        sessionId,
        targetRole.trim(),
        hoursPerWeek
      );

      const normalized = {
        ...result,

        career_twin: {
          current_you:
            result?.career_twin?.current_you?.map((item: any) =>
              typeof item === "string"
                ? item
                : item.title ||
                  item.skill ||
                  item.description ||
                  "Unknown"
            ) || [],

          future_you:
            result?.career_twin?.future_you?.map((item: any) =>
              typeof item === "string"
                ? item
                : item.title ||
                  item.skill ||
                  item.description ||
                  "Unknown"
            ) || [],

          transformation_highlights:
            result?.career_twin?.transformation_highlights?.map(
              (item: any) =>
                typeof item === "string"
                  ? item
                  : `${item.skill}: ${item.description}`
            ) || [],
        },

        skill_gap: {
          matched_skills:
            result?.skill_gap?.strengths || [],

          gaps:
            result?.skill_gap?.priority_gaps?.map((gap: any) => ({
              skill: gap.skill,

              priority:
                gap.importance >= 8
                  ? "critical"
                  : gap.importance >= 6
                  ? "important"
                  : "nice-to-have",

              explanation: gap.description,
            })) || [],
        },
      };

      sessionStorage.setItem(
        "dashboard_data",
        JSON.stringify(normalized)
      );

      sessionStorage.setItem(
        "target_role",
        targetRole.trim()
      );

      console.log(
        "NORMALIZED DASHBOARD DATA",
        normalized
      );

      router.push("/dashboard");
    } catch (err: any) {
      toast({
        title: "Analysis failed",
        description:
          err?.message || "Something went wrong.",
        status: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxW="md" py={20}>
      <VStack spacing={8} align="stretch">
        <VStack spacing={2} textAlign="center">
          <Heading size="lg">
            Set Your Career Target
          </Heading>

          <Text color="gray.600" fontSize="sm">
            Tell CareerOS where you want to go and how much
            time you can invest each week.
          </Text>
        </VStack>

        <FormControl>
          <FormLabel>Target Role</FormLabel>

          <Input
            placeholder="e.g. AI Engineer, Data Analyst, Full Stack Developer"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            bg="white"
          />
        </FormControl>

        <FormControl>
          <FormLabel>
            Time Availability: {hoursPerWeek} hrs/week
          </FormLabel>

          <Slider
            min={2}
            max={40}
            step={1}
            value={hoursPerWeek}
            onChange={setHoursPerWeek}
            colorScheme="blue"
          >
            <SliderTrack>
              <SliderFilledTrack />
            </SliderTrack>

            <SliderThumb />
          </Slider>
        </FormControl>

        <Button
          size="lg"
          bg="gray.900"
          color="white"
          _hover={{ bg: "gray.700" }}
          isLoading={loading}
          loadingText="Running multi-agent analysis..."
          onClick={handleAnalyze}
        >
          Generate My Career Plan
        </Button>
      </VStack>
    </Container>
  );
}