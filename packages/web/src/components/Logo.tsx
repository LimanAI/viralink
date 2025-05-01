import { useRouter } from "next/navigation";
import { LuRocket } from "react-icons/lu";

export default function Logo({ url }: { url: string }) {
  const router = useRouter();
  return (
    <div className="flex items-center space-x-4 cursor-pointer" onClick={() => router.push(url)}>
      <div className="bg-primary h-8 w-8 rounded-full flex items-center justify-center">
        <LuRocket className="w-5 h-5 text-base-100" />
      </div>
      <span className="font-bold text-xl">ViraLink AI</span>
    </div>
  );
}
