import { motion } from "framer-motion";

export function Benefit({
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
      className="bg-white rounded-xl shadow-md hover:shadow-xl p-6 transition-all border-b-4 border-primary group hover:-translate-y-1"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
    >
      <div className="h-14 w-14 rounded-lg bg-primary/10 flex items-center justify-center mb-6 group-hover:bg-primary transition-colors">
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-3">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </motion.div>
  );
}
