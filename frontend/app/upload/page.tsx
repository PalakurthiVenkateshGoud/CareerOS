"use client";

import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  Button,
  Input,
  Icon,
  useToast,
} from "@chakra-ui/react";
import { useRouter } from "next/navigation";
import { useState, useRef } from "react";
import { UploadCloud, FileText } from "lucide-react";
import { uploadResume } from "@/lib/api";

export default function UploadPage() {
  const router = useRouter();
  const toast = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      if (selected.type !== "application/pdf") {
        toast({
          title: "Invalid file type",
          description: "Please upload a PDF resume.",
          status: "error",
        });
        return;
      }
      setFile(selected);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const result = await uploadResume(file);
      sessionStorage.setItem("session_id", result.session_id);
      sessionStorage.setItem("parsed_profile", JSON.stringify(result.parsed_profile));
      router.push("/configure");
    } catch (err: any) {
      toast({
        title: "Upload failed",
        description: err.message || "Something went wrong.",
        status: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxW="md" py={20}>
      <VStack spacing={6} align="stretch">
        <VStack spacing={2} textAlign="center">
          <Heading size="lg">Upload Your Resume</Heading>
          <Text color="gray.600" fontSize="sm">
            We'll extract your skills, projects, and experience to build your
            profile. PDF only.
          </Text>
        </VStack>

        <Box
          border="2px dashed"
          borderColor={file ? "indigo.400" : "gray.300"}
          borderRadius="xl"
          p={10}
          textAlign="center"
          cursor="pointer"
          bg="white"
          onClick={() => fileInputRef.current?.click()}
          _hover={{ borderColor: "indigo.400" }}
        >
          <Icon
            as={file ? FileText : UploadCloud}
            boxSize={10}
            color="indigo.400"
            mb={3}
          />
          <Text fontWeight="semibold">
            {file ? file.name : "Click to select a PDF resume"}
          </Text>
          <Text fontSize="xs" color="gray.500" mt={1}>
            {file ? "Click to change file" : "Max size 10MB"}
          </Text>
          <Input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            display="none"
          />
        </Box>

      <Button
  size="lg"
  bg={file ? "gray.900" : "gray.300"}
  color="white"
  _hover={{ bg: file ? "gray.700" : "gray.300" }}
  cursor={file ? "pointer" : "not-allowed"}
  isLoading={loading}
  loadingText="Analyzing resume..."
  onClick={handleUpload}
>
  Continue
</Button>
      </VStack>
    </Container>
  );
}