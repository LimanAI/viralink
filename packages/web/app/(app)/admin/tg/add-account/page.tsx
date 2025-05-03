"use client";

import { useCallback, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";

import { tgAccountsCreate, tgAccountsSendCode } from "@/api";
import { strError } from "@/utils/errors";

const formSchema = z.object({
  phoneNumber: z.string().min(5, "Phone number is required"),
  apiId: z.coerce.number({ required_error: "Api ID is required" }).gte(-2147483648).lte(2147483647),
  apiHash: z.string().min(5, "Api Hash is required"),
});

type formData = z.infer<typeof formSchema>;

export default function AddAccount() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<formData>({
    resolver: zodResolver(formSchema),
  });

  const onSubmit = useCallback(
    async (data: formData) => {
      setError(null);
      const { data: tgAccount, error } = await tgAccountsCreate({
        body: {
          phone_number: data.phoneNumber,
          api_id: data.apiId,
          api_hash: data.apiHash,
        },
      });
      if (error) {
        setError(strError(error));
        return;
      }

      const { error: sendCodeError } = await tgAccountsSendCode({
        body: { account_id: tgAccount.id, phone_number: data.phoneNumber },
      });
      if (sendCodeError) {
        setError(strError(sendCodeError));
        return;
      }
      router.push(`/admin/tg/add-account/${tgAccount.id}`);
    },
    [setError],
  );

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
              className="alert alert-error alert-soft mb-4"
            >
              <span>{error}</span>
            </motion.div>
          )}
        </AnimatePresence>

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            <div className="form-control flex flex-col space-y-1">
              <label className="label">
                <span className="label-text">Phone number</span>
              </label>
              <input
                type="text"
                placeholder="Enter phone number"
                className="input input-bordered"
                {...register("phoneNumber")}
              />
              {errors.phoneNumber && <span className="text-error text-sm">{errors.phoneNumber.message}</span>}
            </div>

            <div className="form-control flex flex-col space-y-1">
              <label className="label">
                <span className="label-text">App ID</span>
              </label>
              <input
                type="text"
                placeholder="Enter your Api ID"
                className="input input-bordered"
                {...register("apiId")}
              />
              {errors.apiId && <span className="text-error text-sm">{errors.apiId.message}</span>}
            </div>

            <div className="form-control flex flex-col space-y-1">
              <label className="label">
                <span className="label-text">App Hash</span>
              </label>
              <input
                type="text"
                placeholder="Enter your Api Hash"
                className="input input-bordered"
                {...register("apiHash")}
              />
              {errors.apiHash && <span className="text-error text-sm">{errors.apiHash.message}</span>}
            </div>
          </div>

          <div className="flex justify-end mt-8">
            <button type="submit" className="btn btn-primary">
              Next
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
