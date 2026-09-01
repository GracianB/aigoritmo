import "./styles/tokens.css";
import "./styles/studio.css";
import { mountStudio } from "./studio";

const root = document.getElementById("app");
if (!root) throw new Error("#app missing");
void mountStudio(root);
