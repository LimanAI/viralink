import { motion } from "framer-motion";

export function Step({
  index,
  icon,
  title,
  description,
}: {
  index: number;
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <motion.div
      className="flex flex-col items-center text-center"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: index * 0.2 }}
    >
      <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mb-6 relative">
        <span className="text-2xl font-bold text-primary">{index + 1}</span>
        <div className="absolute -right-2 -bottom-2 w-8 h-8 bg-white rounded-full shadow flex items-center justify-center">
          {icon}
        </div>
      </div>
      <h3 className="text-xl font-bold mb-3">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </motion.div>
  );
}
