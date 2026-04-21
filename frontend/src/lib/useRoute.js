import { startTransition, useEffect, useState } from "react";

export function useRoute() {
  const [route, setRoute] = useState(window.location.pathname === "/training" ? "/training" : "/");

  useEffect(() => {
    const onPopState = () => {
      setRoute(window.location.pathname === "/training" ? "/training" : "/");
    };
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  function navigate(nextRoute) {
    if (nextRoute === route) {
      return;
    }
    window.history.pushState({}, "", nextRoute);
    startTransition(() => {
      setRoute(nextRoute);
    });
  }

  return { route, navigate };
}
