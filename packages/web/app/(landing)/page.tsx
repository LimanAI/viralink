"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

// Social media platform data
const platforms = [
  {
    id: "telegram",
    name: "Telegram",
    icon: "📱",
    available: true,
    steps: [
      "You add your channel",
      "Provide instructions for the posts",
      "You setup the bot with publish permissions",
      "You will get adjusted regular posts with your style (we analyze previous posts)",
    ],
  },
  {
    id: "twitter",
    name: "X (Twitter)",
    icon: "𝕏",
    available: false,
  },
  {
    id: "instagram",
    name: "Instagram",
    icon: "📸",
    available: false,
  },
  {
    id: "tiktok",
    name: "TikTok",
    icon: "🎵",
    available: false,
  },
];

// Benefits data
const benefits = [
  {
    title: "No Human Hassle",
    description: "You no longer need to find, hire and work with humans who are unreliable",
    icon: "🤖",
  },
  {
    title: "Fast & Efficient",
    description: "Get your content published quickly without delays or excuses",
    icon: "⚡",
  },
  {
    title: "Cost Effective",
    description: "Save money by automating your social media management",
    icon: "💰",
  },
  {
    title: "Consistent Style",
    description: "Maintain your brand voice and style across all posts",
    icon: "🎨",
  },
];

export default function LandingPage() {
  const [activeTab, setActiveTab] = useState("telegram");

  return (
    <div className="min-h-screen bg-base-100">
      {/* Hero Section */}
      <section className="hero min-h-[70vh] bg-base-200">
        <div className="hero-content text-center">
          <div className="max-w-3xl">
            <h1 className="text-5xl font-bold text-primary">Your AI Social Media Manager</h1>
            <p className="py-6 text-xl">
              ViraLlink AI - SMM AI Agent that allows users to setup their automated social media agents
            </p>
            <button className="btn btn-primary">Get Started</button>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Why Choose ViraLlink AI?</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {benefits.map((benefit, index) => (
              <div key={index} className="card bg-base-200 shadow-xl hover:shadow-2xl transition-all">
                <div className="card-body items-center text-center">
                  <div className="text-4xl mb-4">{benefit.icon}</div>
                  <h3 className="card-title text-primary">{benefit.title}</h3>
                  <p>{benefit.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Social Media Platforms Section */}
      <section className="py-16 px-4 bg-base-200">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Supported Platforms</h2>

          {/* Tabs */}
          <div className="tabs tabs-boxed justify-center mb-8">
            {platforms.map((platform) => (
              <button
                key={platform.id}
                className={`tab tab-lg ${activeTab === platform.id ? "tab-active" : ""}`}
                onClick={() => setActiveTab(platform.id)}
              >
                <span className="mr-2">{platform.icon}</span>
                {platform.name}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <AnimatePresence mode="wait">
                {platforms.map(
                  (platform) =>
                    activeTab === platform.id && (
                      <motion.div
                        key={platform.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        transition={{ duration: 0.3 }}
                        className="flex flex-col md:flex-row gap-8 items-center"
                      >
                        <div className="flex-1">
                          <h3 className="text-2xl font-bold mb-4 flex items-center">
                            <span className="mr-2">{platform.icon}</span>
                            {platform.name}
                          </h3>

                          {platform.available ? (
                            <div>
                              <h4 className="text-xl font-semibold mb-4 text-primary">How It Works</h4>
                              <ul className="space-y-3">
                                {platform.steps?.map((step, index) => (
                                  <li key={index} className="flex items-start">
                                    <span className="badge badge-primary mr-2 mt-1">{index + 1}</span>
                                    <span>{step}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          ) : (
                            <div className="text-center py-8">
                              <div className="text-6xl mb-4">🚧</div>
                              <h4 className="text-xl font-semibold mb-2">Coming Soon</h4>
                              <p>
                                We're working hard to bring {platform.name} integration to ViraLlink AI. Stay tuned!
                              </p>
                            </div>
                          )}
                        </div>

                        <div className="flex-1 flex justify-center">
                          {platform.available ? (
                            <div className="w-full max-w-md h-64 bg-base-300 rounded-lg flex items-center justify-center">
                              <div className="text-center">
                                <div className="text-6xl mb-4">🤖</div>
                                <p className="text-lg">ViraLlink AI for {platform.name}</p>
                              </div>
                            </div>
                          ) : (
                            <div className="w-full max-w-md h-64 bg-base-300 rounded-lg flex items-center justify-center">
                              <div className="text-center">
                                <div className="text-6xl mb-4">⏳</div>
                                <p className="text-lg">Coming Soon</p>
                              </div>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    ),
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to Automate Your Social Media?</h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Join ViraLink AI today and experience the future of social media management.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="btn btn-primary">Get Started</button>
            <button className="btn btn-outline">Learn More</button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer footer-center p-10 bg-base-200 text-base-content">
        <div>
          <p className="font-bold">ViraLink AI</p>
          <p>Copyright © 2024 - All rights reserved</p>
        </div>
      </footer>
    </div>
  );
}
