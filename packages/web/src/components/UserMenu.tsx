export default function UserMenu() {
  return (
    <div className="flex items-center space-x-3">
      <div className="relative">
        <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
          <span className="text-sm font-medium">JS</span>
        </div>
        <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-400 rounded-full border-2 border-white"></div>
      </div>

      <div className="hidden md:block">
        <div className="text-sm font-medium">John Smith</div>
        <div className="text-xs text-gray-500">Administrator</div>
      </div>
    </div>
  );
}
