"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { AnimatePresence, motion } from "framer-motion";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useQuery } from "@tanstack/react-query";

import { tgbotAccountsGet, tgbotAccountsSignin } from "@/api";

const formSchema = z.object({
  password: z.string().optional(),
  code: z.string().length(5, "Code must be 5 digits"),
});

type formData = z.infer<typeof formSchema>;

export default function AddAccountPage() {
  const router = useRouter();
  const { id } = useParams<{ id: string }>();
  const [error, setError] = useState<string | null>(null);

  const {
    isPending,
    isError,
    data: accountData,
    error: getAccountError,
  } = useQuery({
    queryKey: ["/admin/tg/accounts", id],
    retry: false,
    queryFn: async () => {
      const { data } = await tgbotAccountsGet({
        path: { account_id: id },
        throwOnError: true,
      });
      return data;
    },
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<formData>({
    resolver: zodResolver(formSchema),
  });

  const onSubmit = useCallback(
    async (formData: formData) => {
      const { error } = await tgbotAccountsSignin({
        body: {
          account_id: id,
          code: parseInt(formData.code),
          password: formData.password,
        },
      });

      if (error) {
        setError("An error occurred");
      }
    },
    [id, accountData],
  );

  if (isPending) {
    return (
      <div className="bg-base-100 p-10 rounded-lg shadow">
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="loading loading-spinner loading-lg"></div>
          </div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-base-100 p-10 rounded-lg shadow">
        <div className="max-w-2xl mx-auto">
          <span className="alert alert-error alert-soft">Error loading account: {getAccountError.message}</span>
        </div>
      </div>
    );
  }

  if (!accountData) {
    return (
      <div className="bg-base-100 p-10 rounded-lg shadow">
        <div className="max-w-2xl mx-auto">
          <span className="alert alert-error alert-soft">Account not found</span>
        </div>
      </div>
    );
  }

  if (accountData.status === "active") {
    return (
      <div className="bg-base-100 p-10 rounded-lg shadow">
        <div className="max-w-2xl mx-auto">
          <div className="text-center space-y-4">
            <div className="text-success text-6xl mb-4">✓</div>
            <h3 className="text-xl font-semibold">Account Added Successfully!</h3>
            <p className="text-gray-500">Your Telegram account has been successfully connected to ViraLink AI.</p>
            <div className="mt-8">
              <button type="button" onClick={() => router.push("/admin")} className="btn btn-primary">
                Go to Telegram Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (accountData.status !== "sent_code") {
    return (
      <div className="bg-base-100 p-10 rounded-lg shadow">
        <div className="max-w-2xl mx-auto">
          <span className="alert alert-error alert-soft">Improper status: {accountData.status}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-base-100 p-10 rounded-lg shadow">
      <div className="max-w-2xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold">Add Telegram Account</h1>
        </div>

        <AnimatePresence>
          {error && (
            <motion.div
              key="error"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="alert mb-4"
            >
              <span>{error}</span>
            </motion.div>
          )}
        </AnimatePresence>

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            <div className="text-center mb-4">
              <h3 className="text-xl font-semibold">Enter Verification Code</h3>
              <p className="text-gray-500">Please enter the 5-digit code sent to your Telegram</p>
            </div>

            <div className="form-control flex flex-col space-y-1">
              <input
                type="text"
                maxLength={5}
                placeholder="Enter 5-digit code"
                className="input input-bordered text-center text-2xl tracking-widest"
                {...register("code")}
              />
              {errors.code && <span className="text-error text-sm">{errors.code.message}</span>}
            </div>

            <div className="form-control flex flex-col space-y-1">
              <label className="label">
                <span className="label-text">Password</span>
              </label>
              <input
                type="text"
                placeholder="Enter password (optional)"
                className="input input-bordered"
                {...register("password", {
                  setValueAs: (v) => (v === "" ? undefined : v),
                })}
              />
              {errors.password && <span className="text-error text-sm">{errors.password.message}</span>}
            </div>
          </div>

          <div className="flex justify-between mt-8">
            <button type="submit" className="btn btn-primary">
              Next
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
