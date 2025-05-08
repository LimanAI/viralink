import { FiBarChart2 } from "react-icons/fi";

const recommendations = [
  "Add more visual content to increase engagement",
  "Experiment with polls to boost audience interaction",
  "Consider posting at different times to reach a broader audience",
];

export default function RecommendationsBlock() {
  return (
    <>
      <h2 className="text-lg font-semibold mb-3 flex items-center">
        <FiBarChart2 className="mr-2 text-primary" /> Recommendations
      </h2>
      <ul className="space-y-2">
        {recommendations.map((rec, i) => (
          <li key={i} className="flex items-start">
            <span className="mt-0.5 w-6 h-6 bg-primary/20 text-primary rounded-full flex-shrink-0 flex items-center justify-center text-xs mr-2">
              {i + 1}
            </span>
            <span>{rec}</span>
          </li>
        ))}
      </ul>
    </>
  );
}
