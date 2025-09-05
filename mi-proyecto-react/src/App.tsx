import { Button } from "./components/ui/Button";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";

const PlusIcon = () => (
  <svg
    className="w-4 h-4"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 4v16m8-8H4"
    />
  </svg>
);

function App() {
  return (
    <main className="m-10">
      <h1>Mi primero proyecto de React</h1>

      <div>
        <Badge variant="destructive">Badge</Badge>

        <h2>Skeleton ejemplo</h2>
        <div className="flex flex-col space-y-3">
          <Skeleton className="h-[125px] w-[250px] rounded-xl" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-[250px]" />
            <Skeleton className="h-4 w-[200px]" />
          </div>
        </div>
      </div>

      <div className="flex gap-5 mt-5">
        <div>
          <h4>Boton Primary</h4>
          <Button variant="primary">Boton 1</Button>
        </div>
        <div>
          <Button leftIcon={<PlusIcon />} isLoading={true} variant="danger">
            Mi primer boton
          </Button>
        </div>
        <div>
          <Button rightIcon={<PlusIcon />} variant="info" isDisabled={true}>
            Mi segundo boton
          </Button>
        </div>
        <div>
          <Button variant="warning" isLoading={false}>
            Mi segundo boton
          </Button>
        </div>
      </div>
    </main>
  );
}

export default App;
