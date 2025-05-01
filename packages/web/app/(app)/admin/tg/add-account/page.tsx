"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const step1Schema = z.object({
  appId: z.string().min(1, "App ID is required"),
  appHash: z.string().min(1, "App Hash is required"),
});

const step2Schema = z.object({
  code: z.string().length(5, "Code must be 5 digits"),
});

const step3Schema = z.object({
  password: z.string().optional(),
});

type Step1Data = z.infer<typeof step1Schema>;
type Step2Data = z.infer<typeof step2Schema>;
type Step3Data = z.infer<typeof step3Schema>;

function Step1Form({ onSubmit }: { onSubmit: (data: Step1Data) => void }) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<Step1Data>({
    resolver: zodResolver(step1Schema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div className="space-y-4">
        <div className="form-control flex flex-col space-y-1">
          <label className="label">
            <span className="label-text">App ID</span>
          </label>
          <input type="text" placeholder="Enter your App ID" className="input input-bordered" {...register("appId")} />
          {errors.appId && <span className="text-error text-sm">{errors.appId.message}</span>}
        </div>

        <div className="form-control flex flex-col space-y-1">
          <label className="label">
            <span className="label-text">App Hash</span>
          </label>
          <input
            type="text"
            placeholder="Enter your App Hash"
            className="input input-bordered"
            {...register("appHash")}
          />
          {errors.appHash && <span className="text-error text-sm">{errors.appHash.message}</span>}
        </div>
      </div>

      <div className="flex justify-end mt-8">
        <button type="submit" className="btn btn-primary">
          Next
        </button>
      </div>
    </form>
  );
}

function Step2Form({ onSubmit, onBack }: { onSubmit: (data: Step2Data) => void; onBack: () => void }) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<Step2Data>({
    resolver: zodResolver(step2Schema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div className="space-y-4">
        <div className="text-center mb-4">
          <h3 className="text-xl font-semibold">Enter Verification Code</h3>
          <p className="text-gray-500">Please enter the 5-digit code sent to your Telegram</p>
        </div>

        <div className="form-control">
          <input
            type="text"
            maxLength={5}
            placeholder="Enter 5-digit code"
            className="input input-bordered text-center text-2xl tracking-widest"
            {...register("code")}
          />
          {errors.code && <span className="text-error text-sm">{errors.code.message}</span>}
        </div>
      </div>

      <div className="flex justify-between mt-8">
        <button type="button" onClick={onBack} className="btn btn-ghost">
          Back
        </button>
        <button type="submit" className="btn btn-primary">
          Next
        </button>
      </div>
    </form>
  );
}

function Step3Form({ onSubmit, onBack }: { onSubmit: (data: Step3Data) => void; onBack: () => void }) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<Step3Data>({
    resolver: zodResolver(step3Schema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div className="space-y-4">
        <div className="form-control flex flex-col space-y-1">
          <label className="label">
            <span className="label-text">2FA Password (if required)</span>
          </label>
          <input
            type="password"
            placeholder="Enter your 2FA password"
            className="input input-bordered"
            {...register("password")}
          />
          {errors.password && <span className="text-error text-sm">{errors.password.message}</span>}
        </div>
      </div>

      <div className="flex justify-between mt-8">
        <button type="button" onClick={onBack} className="btn btn-ghost">
          Back
        </button>
        <button type="submit" className="btn btn-primary">
          Complete Setup
        </button>
      </div>
    </form>
  );
}

function SuccessStep() {
  return (
    <div className="text-center space-y-4">
      <div className="text-success text-6xl mb-4">✓</div>
      <h3 className="text-xl font-semibold">Account Added Successfully!</h3>
      <p className="text-gray-500">Your Telegram account has been successfully connected to ViraLink AI.</p>
      <div className="mt-8">
        <button type="button" onClick={() => (window.location.href = "/admin")} className="btn btn-primary">
          Go to Telegram Dashboard
        </button>
      </div>
    </div>
  );
}

export default function AddAccount() {
  const [step, setStep] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [_, setFormData] = useState<{
    step1?: Step1Data;
    step2?: Step2Data;
    step3?: Step3Data;
  }>({});

  const handleStep1Submit = (data: Step1Data) => {
    setFormData((prev) => ({ ...prev, step1: data }));
    setStep(2);
  };

  const handleStep2Submit = (data: Step2Data) => {
    setFormData((prev) => ({ ...prev, step2: data }));
    setStep(3);
  };

  const handleStep3Submit = (data: Step3Data) => {
    setFormData((prev) => ({ ...prev, step3: data }));
    setStep(4);
  };

  const goBack = () => {
    setStep((prev) => Math.max(1, prev - 1));
    setError(null);
  };

  return (
    <div className="bg-base-100 p-6 rounded-lg shadow">
      <div className="p-4">
        <div className="max-w-2xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-2xl font-bold">Add Telegram Account</h1>
          </div>

          <AnimatePresence mode="wait">
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="alert alert-error mb-4"
              >
                <span>{error}</span>
              </motion.div>
            )}

            {step === 1 && (
              <motion.div
                key="step1"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <Step1Form onSubmit={handleStep1Submit} />
              </motion.div>
            )}

            {step === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <Step2Form onSubmit={handleStep2Submit} onBack={goBack} />
              </motion.div>
            )}

            {step === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <Step3Form onSubmit={handleStep3Submit} onBack={goBack} />
              </motion.div>
            )}

            {step === 4 && (
              <motion.div key="step4" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
                <SuccessStep />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
