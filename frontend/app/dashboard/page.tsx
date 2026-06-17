"use client";

import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  HStack,
  Spinner,
  Center,
  Button,
} from "@chakra-ui/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import CareerJourneyMap from "@/components/CareerJourneyMap";
import ReadinessGauge from "@/components/ReadinessGauge";
import CareerTwin from "@/components/CareerTwin";
import SkillGapChart from "@/components/SkillGapChart";
import RoadmapTimeline from "@/components/RoadmapTimeline";
import ProjectCard from "@/components/ProjectCard";
import InterviewPrepPanel from "@/components/InterviewPrepPanel";
import AgentTraceViewer from "@/components/AgentTraceViewer";

export default function DashboardPage() {
  const router = useRouter();

  const [data, setData] = useState<any>(null);
  const [targetRole, setTargetRole] = useState("");

  useEffect(() => {
    const raw = sessionStorage.getItem("dashboard_data");
    const role = sessionStorage.getItem("target_role");

    if (!raw) {
      router.push("/upload");
      return;
    }

    try {
      setData(JSON.parse(raw));
      setTargetRole(role || "");
    } catch (err) {
      console.error(err);
    }
  }, [router]);

  if (!data) {
    return (
      <Center h="100vh">
        <Spinner size="xl" />
      </Center>
    );
  }

  return (
    <Container maxW="6xl" py={10}>
      {/* Hide interactive controls when the browser print dialog renders the page */}
      <style jsx global>{`
        @media print {
          .no-print {
            display: none !important;
          }
        }
      `}</style>

      <VStack spacing={6} align="stretch">
        <Box textAlign="center">
          <Heading size="lg">CareerOS Dashboard</Heading>

          {targetRole && (
            <Text mt={2} color="gray.500">
              Target Role: {targetRole}
            </Text>
          )}
        </Box>

        <CareerJourneyMap activeStage="target" />

        {data.readiness && (
          <ReadinessGauge data={data.readiness} />
        )}

        {data.career_twin && (
          <CareerTwin
            data={data.career_twin}
            targetRole={targetRole}
          />
        )}

        {data.skill_gap && (
          <SkillGapChart data={data.skill_gap} />
        )}

        {data.roadmap && (
          <RoadmapTimeline data={data.roadmap} />
        )}

        {data.projects && (
          <ProjectCard projects={data.projects} />
        )}

        {data.interview_prep && (
          <InterviewPrepPanel data={data.interview_prep} />
        )}

        {data.agent_trace && (
          <AgentTraceViewer trace={data.agent_trace} />
        )}

        <HStack spacing={4} justify="center" className="no-print">
          <Button
            variant="outline"
            borderColor="black"
            color="black"
            _hover={{ bg: "blackAlpha.100" }}
            onClick={() => window.print()}
          >
            Print Report
          </Button>

          <Button
            bg="black"
            color="white"
            _hover={{ bg: "gray.800" }}
            onClick={() => router.push("/upload")}
          >
            Start New Analysis
          </Button>
        </HStack>
      </VStack>
    </Container>
  );
}