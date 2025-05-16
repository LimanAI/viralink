"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { FiZap, FiPlus, FiCheck } from "react-icons/fi";
import PageTransition from "@/components/PageTransition";
import { BackButton } from "@/components/BackButton";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useApi } from "@/hooks/useApi";

import {
  CreditsPackage,
  tgbotAuthMe,
  tgCreditsListPackages,
  tgCreditsSendInvoice,
} from "@viralink-ai/sdk";

import { PackageBlock } from "./_components/PackageBlock";

export default function Payment() {
  const [selectedPackage, setSelectedPackage] = useState<CreditsPackage | null>(
    null
  );
  // TODO:
  const success = false;

  const api = useApi();

  const { data: user } = useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      const { data } = await tgbotAuthMe({
        throwOnError: true,
      });
      return data;
    },
    enabled: !!api,
  });

  const { data: packages } = useQuery({
    queryKey: ["packages"],
    queryFn: async () => {
      if (!api) throw new Error("API not initialized");
      const { data } = await tgCreditsListPackages({
        throwOnError: true,
      });
      return data;
    },
    enabled: !!api,
  });

  const { mutate: purchase, isPending: processing } = useMutation({
    mutationFn: async (pkg: CreditsPackage | null) => {
      if (!api) throw new Error("API not initialized");
      if (!pkg) throw new Error("Package not selected");

      await tgCreditsSendInvoice({
        body: {
          package_name: pkg.package_name,
        },
        throwOnError: true,
      });
    },
    onSuccess: () => {},
  });

  // Staggered animation for packages
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  return (
    <PageTransition>
      <BackButton href="/" />
      <div className="container mx-auto max-w-md p-4">
        <div className="flex items-center mb-6">
          <h1 className="text-2xl font-bold">Credits</h1>
        </div>

        <div className="card bg-base-200 p-4 mb-8">
          <div className="flex justify-center items-center mb-2">
            <div className="text-3xl text-secondary-content mr-3"></div>
            <div className="text-center">
              <div className="text-sm opacity-70">Your current balance</div>
              <div className="flex flex-row text-4xl my-2">
                <FiZap className="h-10 w-10 text-secondary-content mr-2" />
                <div className="font-bold">
                  {user?.credits_balance.toLocaleString()}
                </div>
              </div>
            </div>
          </div>
          <p className="text-center text-sm opacity-70">
            Credits are used to generate content and power your bots
          </p>
        </div>

        {/* Success message */}
        {success && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="alert alert-success mb-6 shadow-md"
          >
            <FiCheck className="stroke-current flex-shrink-0 h-6 w-6" />
            <span>Purchase successful! Credits added to your account.</span>
          </motion.div>
        )}

        <h2 className="text-xl font-semibold mb-4">Select a package</h2>
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="space-y-4"
        >
          {packages?.map((pkg, i) => (
            <PackageBlock
              key={pkg.package_name}
              pkg={pkg}
              index={i}
              isSelected={selectedPackage?.package_name === pkg.package_name}
              onPackageSelect={(pkg: CreditsPackage) => setSelectedPackage(pkg)}
            />
          ))}
        </motion.div>

        <div className="mt-6 bg-base-100">
          <button
            onClick={() => purchase(selectedPackage)}
            disabled={!selectedPackage || processing}
            className="btn btn-primary w-full"
          >
            {processing ? (
              <>
                <span className="loading loading-spinner loading-sm mr-2"></span>
                Processing...
              </>
            ) : (
              <>
                <FiPlus className="mr-2" />
                {selectedPackage
                  ? `Buy ${selectedPackage.credits_amount.toLocaleString()} Credits for ☆ ${selectedPackage.stars_amount.toLocaleString()}`
                  : "Select a package"}
              </>
            )}
          </button>
        </div>
      </div>
    </PageTransition>
  );
}
