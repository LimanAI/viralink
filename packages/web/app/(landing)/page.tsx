"use client";

import { motion } from "framer-motion";
import {
  LuRocket,
  LuDollarSign,
  LuPaintBucket,
  LuSettings,
  LuLink,
  LuCheck,
  LuChartNoAxesColumnIncreasing,
  LuChevronRight,
} from "react-icons/lu";
import { RiRobot2Line } from "react-icons/ri";
import { FiZap } from "react-icons/fi";
import { PiTelegramLogo, PiXLogoBold, PiInstagramLogo } from "react-icons/pi";
import { BiLogoTiktok } from "react-icons/bi";
import Image from "next/image";

import { Benefit } from "./_components/Benefit";
import { Platforms, TPlatform } from "./_components/Platforms";
import { Step } from "./_components/Step";

// Social media platform data
const platforms: TPlatform[] = [
  {
    id: "telegram",
    name: "Telegram",
    icon: <PiTelegramLogo className="w-6 h-6" />,
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
    icon: <PiXLogoBold className="w-6 h-6" />,
    available: false,
  },
  {
    id: "instagram",
    name: "Instagram",
    icon: <PiInstagramLogo className="w-7 h-7" />,
    available: false,
  },
  {
    id: "tiktok",
    name: "TikTok",
    icon: <BiLogoTiktok className="w-6 h-6" />,
    available: false,
  },
];

// Benefits data
const benefits = [
  {
    title: "No Human Hassle",
    description: "You no longer need to find, hire and work with humans who are unreliable",
    icon: <RiRobot2Line className="w-6 h-6 text-primary group-hover:text-white transition-colors" />,
  },
  {
    title: "Fast & Efficient",
    description: "Get your content published quickly without delays or excuses",
    icon: <FiZap className="w-6 h-6 text-primary group-hover:text-white transition-colors" />,
  },
  {
    title: "Cost Effective",
    description: "Save money by automating your social media management",
    icon: <LuDollarSign className="w-6 h-6 text-primary group-hover:text-white transition-colors" />,
  },
  {
    title: "Consistent Style",
    description: "Maintain your brand voice and style across all posts",
    icon: <LuPaintBucket className="w-6 h-6 text-primary group-hover:text-white transition-colors" />,
  },
];

// Workflow steps
const workflowSteps = [
  {
    title: "Connect Platforms",
    description: "Link your social media accounts to ViraLlink AI and grant necessary permissions.",
    icon: <LuLink className="w-5 h-5 text-primary" />,
  },
  {
    title: "Configure Your AI",
    description: "Set your content preferences, posting schedule, and target audience parameters.",
    icon: <LuSettings className="w-5 h-5 text-primary" />,
  },
  {
    title: "Let AI Work",
    description: "Our AI generates, schedules, and publishes content automatically based on your settings.",
    icon: <LuRocket className="w-5 h-5 text-primary" />,
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white sticky top-0 z-50 shadow-sm">
        <div className="container mx-auto px-4 py-3">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <div className="bg-primary h-8 w-8 rounded-full flex items-center justify-center">
                <LuRocket className="w-5 h-5 text-white" />
              </div>
              <span className="font-heading font-bold text-xl">ViraLink AI</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="font-medium hover:text-primary transition-colors">
                Features
              </a>
              <a href="#platforms" className="font-medium hover:text-primary transition-colors">
                Platforms
              </a>
              <a href="#how-it-works" className="font-medium hover:text-primary transition-colors">
                How It Works
              </a>
            </div>
            <div className="flex items-center space-x-4">
              <a href="#" className="hidden md:inline-block text-sm font-medium hover:text-primary transition-colors">
                Login
              </a>
              <a
                href="#"
                className="bg-primary hover:bg-primary/90 text-neutral-900 font-semibold px-5 py-2 rounded-full transition-colors shadow-sm hover:shadow-md"
              >
                Get Started
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative bg-gradient-to-b from-primary/10 to-white overflow-hidden pt-16 pb-32">
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-primary/30 rounded-full opacity-50 blur-3xl"></div>
        <div className="absolute top-32 -left-32 w-72 h-72 bg-primary/20 rounded-full opacity-40 blur-3xl"></div>

        <div className="container mx-auto px-4 relative z-10">
          <div className="flex flex-col lg:flex-row items-center gap-12">
            <div className="lg:w-1/2 space-y-8">
              <div className="inline-block bg-primary/20 px-4 py-2 rounded-full mb-2">
                <span className="text-sm font-semibold text-primary/90 flex items-center">
                  <FiZap className="w-4 h-4 mr-2" /> Automate Your Social Media
                </span>
              </div>
              <h1 className="font-heading text-4xl md:text-5xl lg:text-6xl font-bold leading-tight">
                Your <span className="text-primary">AI Social Media</span> Manager
              </h1>
              <p className="text-lg md:text-xl text-gray-600 max-w-xl">
                Let ViraLlink AI handle your social media presence with intelligent content creation, scheduling, and
                analytics - all on autopilot.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <a
                  href="#"
                  className="inline-block bg-primary hover:bg-primary/90 text-neutral-900 font-semibold px-8 py-3 rounded-full text-center transition-colors shadow-md hover:shadow-lg"
                >
                  Get Started Free
                </a>
                <a
                  href="#how-it-works"
                  className="inline-block border-2 border-neutral-800 hover:border-primary hover:text-primary font-semibold px-8 py-3 rounded-full text-center transition-colors"
                >
                  <span className="flex items-center justify-center">
                    <span>How It Works</span>
                    <LuChevronRight className="w-5 h-5 ml-2" />
                  </span>
                </a>
              </div>
              {/*
              <div className="flex items-center space-x-4 pt-4">
                <div className="flex -space-x-2">
                  <div className="w-8 h-8 rounded-full border-2 border-white bg-gray-300"></div>
                  <div className="w-8 h-8 rounded-full border-2 border-white bg-gray-300"></div>
                  <div className="w-8 h-8 rounded-full border-2 border-white bg-gray-300"></div>
                </div>
                <div className="text-sm text-gray-600">
                  <span className="font-semibold text-neutral-800">500+</span> creators trust us
                </div>
              </div>
              */}
            </div>
            <div className="lg:w-1/2 flex justify-center">
              <div className="relative max-w-lg">
                {/* Main image */}
                <motion.div
                  className="relative z-10"
                  animate={{ y: [0, -10, 0] }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    repeatType: "loop",
                  }}
                >
                  <div className="rounded-xl shadow-2xl border-4 border-white bg-gray-300 w-[500px] h-[375px]">
                    {/*
                    <Image
                      src="https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7"
                      alt="ViraLink AI"
                      fill={true}
                      className="rounded-xl"
                    />
                    */}
                  </div>

                  {/* Floating elements */}
                  <motion.div
                    className="absolute -top-6 -right-6 bg-white p-3 rounded-lg shadow-lg"
                    animate={{ y: [0, -5, 0] }}
                    transition={{
                      duration: 2,
                      delay: 0.5,
                      repeat: Infinity,
                      repeatType: "loop",
                    }}
                  >
                    <div className="flex items-center space-x-2">
                      <div className="bg-green-500 h-6 w-6 rounded-full flex items-center justify-center">
                        <LuCheck className="w-4 h-4 text-white" />
                      </div>
                      <span className="font-medium">Post Scheduled</span>
                    </div>
                  </motion.div>

                  <motion.div
                    className="absolute -bottom-4 -left-6 bg-white p-3 rounded-lg shadow-lg"
                    animate={{ y: [0, -5, 0] }}
                    transition={{
                      duration: 2,
                      delay: 1,
                      repeat: Infinity,
                      repeatType: "loop",
                    }}
                  >
                    <div className="flex items-center space-x-2">
                      <div className="text-primary">
                        <LuChartNoAxesColumnIncreasing className="w-5 h-5" />
                      </div>
                      <span className="font-medium">+24% Engagement</span>
                    </div>
                  </motion.div>
                </motion.div>

                {/* Background decorations */}
                <div className="absolute -bottom-10 -right-10 h-40 w-40 bg-primary opacity-20 rounded-full blur-md"></div>
                <div className="absolute -z-10 -top-5 -left-5 h-40 w-40 bg-primary/60 opacity-20 rounded-full blur-md"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section id="features" className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Why Choose ViraLink AI?</h2>
            <p className="text-lg text-gray-600">
              Experience the future of social media management with our AI-powered platform
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {benefits.map((benefit, index) => (
              <Benefit key={index} index={index} {...benefit} />
            ))}
          </div>
        </div>
      </section>

      {/* Platforms Section */}
      <section id="platforms" className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Supported Platforms</h2>
            <p className="text-lg text-gray-600">
              Connect your social media accounts and let ViraLink AI handle the rest.
            </p>
          </div>

          <Platforms platforms={platforms} />
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">How ViraLink AI Works</h2>
            <p className="text-lg text-gray-600">
              Our powerful AI analyzes your existing content and audience to create engaging posts that match your
              style.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {workflowSteps.map((step, index) => (
              <Step key={index} index={index} {...step} />
            ))}
          </div>

          <div className="mt-16 text-center">
            <a
              href="#"
              className="inline-block bg-primary hover:bg-primary/90 text-neutral-900 font-semibold px-8 py-3 rounded-full transition-colors shadow-md hover:shadow-lg"
            >
              Get Started Now
            </a>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4 text-neutral-900">Ready to Automate Your Social Media?</h2>
          <p className="text-lg text-neutral-800 mb-8 max-w-2xl mx-auto">
            Join ViraLlink AI today and experience the future of social media management. Start your free trial now.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="#"
              className="bg-neutral-900 hover:bg-neutral-800 text-white font-semibold px-8 py-3 rounded-full transition-colors shadow-md hover:shadow-lg"
            >
              Get Started Free
            </a>
            <a
              href="#"
              className="bg-white hover:bg-gray-100 text-neutral-900 font-semibold px-8 py-3 rounded-full transition-colors shadow-md hover:shadow-lg"
            >
              Schedule Demo
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-neutral-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="bg-primary h-8 w-8 rounded-full flex items-center justify-center">
                  <LuRocket className="w-5 h-5 text-neutral-900" />
                </div>
                <span className="font-heading font-bold text-xl">ViraLink AI</span>
              </div>
              <p className="text-gray-400">
                AI-powered social media management platform that automates content creation and publishing.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2">
                <li>
                  <a href="#" className="text-gray-400 hover:text-white transition-colors">
                    Features
                  </a>
                </li>
                <li>
                  <a href="#" className="text-gray-400 hover:text-white transition-colors">
                    Pricing
                  </a>
                </li>
                <li>
                  <a href="#" className="text-gray-400 hover:text-white transition-colors">
                    Integrations
                  </a>
                </li>
                <li>
                  <a href="#" className="text-gray-400 hover:text-white transition-colors">
                    Roadmap
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Resources</h4>
              <ul className="space-y-2">
                <li>
                  <a href="#" className="text-gray-400 hover:text-white transition-colors">
                    Blog
                  </a>
                </li>
                <li>
                  <a href="#" className="text-gray-400 hover:text-white transition-colors">
                    Documentation
                  </a>
                </li>
                <li>
                  <a href="#" className="text-gray-400 hover:text-white transition-colors">
                    Help Center
                  </a>
                </li>
                <li>
                  <a href="#" className="text-gray-400 hover:text-white transition-colors">
                    API
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2">
                <li>
                  <a href="#" className="text-gray-400 hover:text-white transition-colors">
                    About Us
                  </a>
                </li>
                <li>
                  <a href="#" className="text-gray-400 hover:text-white transition-colors">
                    Careers
                  </a>
                </li>
                <li>
                  <a href="#" className="text-gray-400 hover:text-white transition-colors">
                    Contact
                  </a>
                </li>
                <li>
                  <a href="#" className="text-gray-400 hover:text-white transition-colors">
                    Terms & Privacy
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-12 pt-8 text-center text-gray-400">
            <p>© 2025 ViraLink AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
