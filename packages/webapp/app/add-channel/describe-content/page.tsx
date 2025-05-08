"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import PageTransition from "@/components/PageTransition";
import { motion } from "framer-motion";
import { FiCheck, FiFileText, FiCalendar, FiRepeat, FiArrowLeft } from "react-icons/fi";

interface Channel {
  name: string;
  id: string;
}

interface Bot {
  name: string;
  id: string;
}

export default function DescribeContent() {
  const router = useRouter();
  const [channel, setChannel] = useState<Channel | null>(null);
  const [bot, setBot] = useState<Bot | null>(null);
  const [contentType, setContentType] = useState<string[]>([]);
  const [frequency, setFrequency] = useState("daily");
  const [topics, setTopics] = useState("");

  // Content type options
  const contentTypeOptions = [
    { id: "text", label: "Text Posts" },
    { id: "images", label: "Images" },
    { id: "videos", label: "Videos" },
    { id: "polls", label: "Polls" },
    { id: "news", label: "News" },
    { id: "tutorials", label: "Tutorials" },
  ];

  // Frequency options
  const frequencyOptions = [
    { id: "daily", label: "Daily" },
    { id: "weekly", label: "Weekly" },
    { id: "multiple", label: "2-3 times a week" },
    { id: "custom", label: "Custom Schedule" },
  ];

  // Form validation
  const isContentTypeValid = contentType.length > 0;
  const isTopicsValid = topics.length >= 10;
  const isFormValid = isContentTypeValid && frequency && isTopicsValid;

  useEffect(() => {
    // Get the selected channel and bot from localStorage
    if (typeof window !== "undefined") {
      const channelData = localStorage.getItem("selectedChannel");
      const botData = localStorage.getItem("selectedBot");

      if (channelData) {
        setChannel(JSON.parse(channelData));
      } else {
        // If no channel selected, go back to selection page
        router.push("/add-channel");
        return;
      }

      if (botData) {
        setBot(JSON.parse(botData));
      } else {
        // If no bot selected, go back to bot selection
        router.push("/add-channel/select-bot");
        return;
      }
    }
  }, [router]);

  const handleConnectBot = async () => {
    try {
      // Get all necessary data
      const channelData = localStorage.getItem("selectedChannel");
      const botData = localStorage.getItem("selectedBot");
      const personaData = localStorage.getItem("channelPersona");
      
      if (!channelData || !botData || !personaData) {
        throw new Error("Missing required data");
      }

      const contentData = {
        contentType,
        frequency,
        topics,
      };

      // Store content preferences in localStorage
      localStorage.setItem("channelContent", JSON.stringify(contentData));

      // Navigate to success page
      router.push("/add-channel/success");
    } catch (err) {
      console.error("Failed to connect bot:", err);
    }
  };

  const toggleContentType = (type: string) => {
    if (contentType.includes(type)) {
      setContentType(contentType.filter((t) => t !== type));
    } else {
      setContentType([...contentType, type]);
    }
  };

  return (
    <PageTransition>
      <div className="container mx-auto max-w-md p-4">
        <div className="flex items-center mb-6">
          <button
            onClick={() => router.push("/add-channel/describe-persona")}
            className="btn btn-ghost btn-circle"
          >
            <FiArrowLeft className="text-xl" />
          </button>
          <h1 className="text-2xl font-bold ml-2">Content Preferences</h1>
        </div>
        
        <p className="text-sm opacity-70 mb-6">
          Tell {bot?.name || "your bot"} what kind of content to create for{" "}
          {channel?.name || "your channel"}
        </p>

        <div className="form-control mb-6">
          <label className="label">
            <span className="label-text font-medium flex items-center">
              <FiFileText className="mr-2" /> Content Types
            </span>
          </label>

          <div className="grid grid-cols-2 gap-2 mt-1">
            {contentTypeOptions.map((option) => (
              <div
                key={option.id}
                className={`flex items-center p-3 rounded-lg cursor-pointer transition-all ${
                  contentType.includes(option.id)
                    ? "bg-primary bg-opacity-10 border border-primary"
                    : "bg-base-200 border border-base-200"
                }`}
                onClick={() => toggleContentType(option.id)}
              >
                <div
                  className={`w-4 h-4 rounded-md flex items-center justify-center mr-2 ${
                    contentType.includes(option.id)
                      ? "bg-primary"
                      : "bg-base-300"
                  }`}
                >
                  {contentType.includes(option.id) && (
                    <FiCheck className="text-xs text-white" />
                  )}
                </div>
                <span>{option.label}</span>
              </div>
            ))}
          </div>

          {contentType.length === 0 && (
            <label className="label">
              <span className="label-text-alt text-error">
                Please select at least one content type
              </span>
            </label>
          )}
        </div>

        <div className="form-control mb-6">
          <label className="label">
            <span className="label-text font-medium flex items-center">
              <FiRepeat className="mr-2" /> Posting Frequency
            </span>
          </label>

          <div className="grid grid-cols-2 gap-2 mt-1">
            {frequencyOptions.map((option) => (
              <div
                key={option.id}
                className={`flex items-center p-3 rounded-lg cursor-pointer transition-all ${
                  frequency === option.id
                    ? "bg-primary bg-opacity-10 border border-primary"
                    : "bg-base-200 border border-base-200"
                }`}
                onClick={() => setFrequency(option.id)}
              >
                <div
                  className={`w-4 h-4 rounded-full flex items-center justify-center mr-2 ${
                    frequency === option.id ? "bg-primary" : "bg-base-300"
                  }`}
                >
                  {frequency === option.id && (
                    <FiCheck className="text-xs text-white" />
                  )}
                </div>
                <span>{option.label}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="form-control mb-8">
          <label className="label">
            <span className="label-text font-medium flex items-center">
              <FiCalendar className="mr-2" /> Content Topics & Themes
            </span>
          </label>
          <textarea
            placeholder="Describe topics your content should cover..."
            className={`textarea textarea-bordered w-full h-32 ${!topics || isTopicsValid ? "" : "textarea-error"}`}
            value={topics}
            onChange={(e) => setTopics(e.target.value)}
          ></textarea>
          <label className="label">
            <span className="label-text-alt">
              {topics && !isTopicsValid
                ? "Description too short (min 10 characters)"
                : 'E.g., "Latest AI research, machine learning tutorials, industry news"'}
            </span>
          </label>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card bg-base-200 p-4 mb-6"
        >
          <h3 className="font-semibold mb-2">What happens next:</h3>
          <p className="text-sm opacity-80">
            After connecting, your bot will prepare content based on your
            preferences. You'll be able to review and approve all posts before
            they're published.
          </p>
        </motion.div>

        <button
          className="btn btn-primary w-full"
          onClick={handleConnectBot}
          disabled={!isFormValid}
        >
          Connect Bot
        </button>
      </div>
    </PageTransition>
  );
}
