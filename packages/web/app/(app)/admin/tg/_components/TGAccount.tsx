import clsx from "clsx";

export default function TGAccount({ id, status }: { id: string; status: string }) {
  return (
    <div className="card w-96 bg-base-200 shadow-sm">
      <div className="card-body">
        <span
          className={clsx("badge badge-xs", {
            "badge-warning": status === "inactive",
            "badge-success": status === "active",
          })}
        >
          {status}
        </span>

        <h2 className="text-md font-bold">{id}</h2>
        {/*
        <ul className="mt-6 flex flex-col gap-1 text-xs">
          <li>
            <span>Created 30 days ago</span>
          </li>
          <li>
            <span>Added to 81 channels</span>
          </li>
        </ul>
        */}
      </div>
    </div>
  );
}
