"use client";
import {
  Box,
  Heading,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  VStack,
  Text,
} from "@chakra-ui/react";

interface InterviewQuestion {
  question: string;
  what_interviewer_is_assessing: string;
}

interface InterviewData {
  hr_questions: InterviewQuestion[];
  technical_questions: InterviewQuestion[];
  project_questions: InterviewQuestion[];
}

function QuestionList({ questions }: { questions: InterviewQuestion[] }) {
  return (
    <VStack align="stretch" spacing={4}>
      {questions?.map((q, i) => (
        <Box key={i} borderWidth="1px" borderRadius="md" p={3}>
          <Text fontWeight="semibold" mb={1}>
            {i + 1}. {q.question}
          </Text>
          <Text fontSize="xs" color="gray.500">
            Assessing: {q.what_interviewer_is_assessing}
          </Text>
        </Box>
      ))}
    </VStack>
  );
}

export default function InterviewPrepPanel({ data }: { data: InterviewData }) {
  return (
    <Box bg="white" borderRadius="2xl" p={6} shadow="md">
      <Heading size="md" mb={4}>
        Interview Preparation
      </Heading>

      <Tabs colorScheme="indigo">
        <TabList>
          <Tab>HR / Behavioral</Tab>
          <Tab>Technical</Tab>
          <Tab>Project-Based</Tab>
        </TabList>

        <TabPanels>
          <TabPanel px={0}>
            <QuestionList questions={data.hr_questions} />
          </TabPanel>
          <TabPanel px={0}>
            <QuestionList questions={data.technical_questions} />
          </TabPanel>
          <TabPanel px={0}>
            <QuestionList questions={data.project_questions} />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
}