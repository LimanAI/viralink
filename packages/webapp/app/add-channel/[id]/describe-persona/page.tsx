"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import PageTransition from "@/components/PageTransition";
import { motion } from "framer-motion";
import { FiUser, FiTarget, FiMessageSquare, FiCheck, FiArrowLeft } from "react-icons/fi";

export default function DescribePersona() {
  const router = useRouter();
  const [channel, setChannel] = useState(null);
  const [bot, setBot] = useState(null);
  const [tone, setTone] = useState("professional");
  const [audience, setAudience] = useState("");
  const [notes, setNotes] = useState("");

  // Tone options
  const toneOptions = [
    { id: "professional", label: "Professional" },
    { id: "friendly", label: "Friendly & Casual" },
    { id: "humorous", label: "Humorous" },
    { id: "inspirational", label: "Inspirational" },
    { id: "educational", label: "Educational" },
  ];

  // Form validation
  const isAudienceValid = audience.length >= 5;
  const isFormValid = tone && isAudienceValid;

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

  const handleSubmit = () => {
    if (isFormValid) {
      // Store persona data and move to next step
      if (typeof window !== "undefined") {
        localStorage.setItem(
          "channelPersona",
          JSON.stringify({
            tone,
            audience,
            notes,
          })
        );
      }
      router.push("/add-channel/describe-content");
    }
  };

  const handleBack = () => {
    router.push("/add-channel/select-bot");
  };

  return (
    <PageTransition>
      <div className="container mx-auto max-w-md p-4">
        <div className="flex items-center mb-6">
          <button
            onClick={handleBack}
            className="btn btn-ghost btn-sm mr-2"
          >
            <FiArrowLeft className="text-lg" />
          </button>
          <h1 className="text-2xl font-bold">Define Your Channel Persona</h1>
        </div>
        <p className="text-sm opacity-70 mb-6">
          Help {bot?.name || "your bot"} understand the voice and style for{" "}
          {channel?.name || "your channel"}
        </p>

        <div className="form-control mb-6">
          <label className="label">
            <span className="label-text font-medium flex items-center">
              <FiMessageSquare className="mr-2" /> Communication Tone
            </span>
          </label>

          <div className="grid grid-cols-2 gap-2 mt-1">
            {toneOptions.map((option) => (
              <div
                key={option.id}
                className={`flex items-center p-3 rounded-lg cursor-pointer transition-all ${
                  tone === option.id
                    ? "bg-primary bg-opacity-10 border border-primary"
                    : "bg-base-200 border border-base-200"
                }`}
                onClick={() => setTone(option.id)}
              >
                <div
                  className={`w-4 h-4 rounded-full flex items-center justify-center mr-2 ${
                    tone === option.id ? "bg-primary" : "bg-base-300"
                  }`}
                >
                  {tone === option.id && (
                    <FiCheck className="text-xs text-white" />
                  )}
                </div>
                <span>{option.label}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="form-control mb-6">
          <label className="label">
            <span className="label-text font-medium flex items-center">
              <FiTarget className="mr-2" /> Target Audience
            </span>
          </label>
          <textarea
            placeholder="Describe who your content is for..."
            className={`textarea textarea-bordered w-full h-24 ${!audience || isAudienceValid ? "" : "textarea-error"}`}
            value={audience}
            onChange={(e) => setAudience(e.target.value)}
          ></textarea>
          <label className="label">
            <span className="label-text-alt">
              {audience && !isAudienceValid
                ? "Description too short (min 5 characters)"
                : 'E.g., "Tech professionals in their 30s interested in AI advancements"'}
            </span>
          </label>
        </div>

        <div className="form-control mb-8">
          <label className="label">
            <span className="label-text font-medium flex items-center">
              <FiUser className="mr-2" /> Additional Notes (Optional)
            </span>
          </label>
          <textarea
            placeholder="Any specific guidance for your bot..."
            className="textarea textarea-bordered w-full h-24"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          ></textarea>
          <label className="label">
            <span className="label-text-alt">
              E.g., "Include statistics in posts when relevant"
            </span>
          </label>
        </div>

        <div className="flex justify-end mt-8">
          <button
            onClick={handleSubmit}
            disabled={!isFormValid}
            className={`btn btn-primary ${!isFormValid ? 'btn-disabled' : ''}`}
          >
            Continue
          </button>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card bg-base-200 p-4 mt-8"
        >
          <h3 className="font-semibold mb-2">Why this matters:</h3>
          <p className="text-sm opacity-80">
            Defining a clear persona ensures all content from your bot maintains
            a consistent voice that resonates with your audience and represents
            your brand effectively.
          </p>
        </motion.div>
      </div>
    </PageTransition>
  );
}
