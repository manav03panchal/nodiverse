import { useState, useEffect, useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { GraphData, User } from "./types";
import * as d3 from "d3"; // Import d3

function App() {
  const [graphData, setGraphData] = useState<GraphData>({
    nodes: [],
    links: [],
  });
  const [connectionStatus, setConnectionStatus] =
    useState<string>("disconnected");
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [hoveredNode, setHoveredNode] = useState<User | null>(null);
  const [eventName] = useState("HackED");
  const graphRef = useRef(null);
  const [windowSize, setWindowSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  const loggedInUserId = "73ae7869-7c57-40a7-b620-46bcad9f11b0";

  useEffect(() => {
    const eventId = "5f40798c-ed95-4b11-bcc3-5ab6b4a4badb";
    const socket = new WebSocket(
      `ws://${window.location.hostname}:8000/ws/${eventId}/${loggedInUserId}`
    );

    socket.onopen = () => {
      console.log("WebSocket connection opened");
      setConnectionStatus("🟢 Connected");
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === "initial_state") {
          const nodes = data.data.participants.map((p: any) => ({
            id: p.id,
            name: p.name || `User ${p.id.substring(0, 5)}`,
            role: p.role,
            profile: p.profile,
            color:
              p.id === loggedInUserId
                ? "#ffcc00"
                : p.role === "organizer"
                  ? "#e63946"
                  : "#457b9d",
          }));

          setGraphData({ nodes, links: [] });
        }

        if (data.type === "new_user") {
          setGraphData((prevData) => {
            const newNode = {
              id: data.user.id,
              name: data.user.name || data.user.id,
              role: data.user.role,
              profile: data.user.profile,
              color:
                data.user.id === loggedInUserId
                  ? "#ffcc00"
                  : data.user.role === "organizer"
                    ? "#e63946"
                    : "#457b9d",
            };

            if (!prevData.nodes.find((node) => node.id === newNode.id)) {
              return {
                nodes: [...prevData.nodes, newNode],
                links: [
                  ...prevData.links,
                  { source: eventId, target: newNode.id },
                ],
              };
            }
            return prevData;
          });
        }
      } catch (error) {
        console.error("Error processing message:", error);
      }
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
      setConnectionStatus("🔴 Error");
    };

    socket.onclose = () => {
      console.log("WebSocket closed");
      setConnectionStatus("⚪ Disconnected");
    };

    return () => {
      socket.close();
    };
  }, []);

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  const handleNodeClick = (node: any) => {
    if (node.role) {
      setSelectedUser(node);
    }
  };

  // Calculate the graph dimensions based on the window size
  const graphWidth = Math.max(windowSize.width - 320, 480); // Sidebar width is 320px
  const graphHeight = Math.max(windowSize.height - 120, 400); // Header and footer height

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.headerTitle}>Nodiverse</h1>
      </header>

      <div style={styles.mainContent}>
        <aside style={styles.sidebar}>
          <h2 style={styles.sidebarTitle}>
            {selectedUser ? selectedUser.name : "Select a User"}
          </h2>
          {selectedUser ? (
            <>
              <p style={styles.text}>
                <strong>Role:</strong> {selectedUser.role.toUpperCase()}
              </p>
              {selectedUser.profile?.github && (
                <a
                  href={selectedUser.profile.github}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={styles.link}
                  onClick={(e) => e.stopPropagation()}
                >
                  GitHub →
                </a>
              )}
              <button
                onClick={() => setSelectedUser(null)}
                style={styles.closeButton}
              >
                ✖ Close
              </button>
            </>
          ) : (
            <p style={styles.text}>Click on a user to view details.</p>
          )}
        </aside>

        <div
          style={{
            width: graphWidth,
            height: graphHeight,
            position: "relative",
            margin: "20px 0", // Adjusted margin for cleaner look
            boxSizing: "border-box",
          }}
        >
          <ForceGraph2D
            ref={graphRef}
            graphData={graphData}
            nodeLabel={() => ""}
            nodeColor={(node) => node.color}
            onNodeClick={handleNodeClick}
            onNodeHover={(node) => setHoveredNode(node || null)}
            width={graphWidth}
            height={graphHeight}
            linkDirectionalArrowLength={4}
            linkDirectionalArrowRelPos={1}
            nodeCanvasObjectMode={(node) =>
              hoveredNode?.id === node.id ? "before" : undefined
            }
            nodeCanvasObject={(node, ctx, globalScale) => {
              if (hoveredNode?.id === node.id) {
                const label = node.name;
                const fontSize = 12 / globalScale;
                ctx.font = `${fontSize}px Iosevka`;
                ctx.textAlign = "center";
                ctx.textBaseline = "top";
                ctx.fillStyle = "#fff";
                ctx.fillText(label, node.x!, node.y! + 10);
              }
            }}
            d3ForceCollide={(node) => 20}
            d3ForceX={d3.forceX().strength(0.1)}
            d3ForceY={d3.forceY().strength(0.1)}
            d3ForceCharge={-30}
            linkDirectionalParticles={2}
            linkDirectionalParticleWidth={4}
            linkDistance={50}
            centerAt={{ x: graphWidth / 2, y: graphHeight / 2 }}
            renderCustomCanvas={(ctx, scale) => {
              if (!graphRef.current) return;
              const fg = graphRef.current;
              const nodes = fg.graphData().nodes;

              if (nodes.length === 0) return;

              let minX = Infinity,
                maxX = -Infinity,
                minY = Infinity,
                maxY = -Infinity;

              nodes.forEach((node) => {
                if (node.role) {
                  minX = Math.min(minX, node.x);
                  maxX = Math.max(maxX, node.x);
                  minY = Math.min(minY, node.y);
                  maxY = Math.max(maxY, node.y);
                }
              });

              minX = Math.max(minX, 0);
              maxX = Math.min(maxX, graphWidth);
              minY = Math.max(minY, 0);
              maxY = Math.min(maxY, graphHeight);

              ctx.strokeStyle = "#fff";
              ctx.lineWidth = 4;
              ctx.strokeRect(minX, minY, maxX - minX, maxY - minY);

              ctx.font = "16px Iosevka";
              ctx.fillStyle = "#fff";
              ctx.textAlign = "center";
              ctx.fillText(eventName, (minX + maxX) / 2, minY - 15);
            }}
            onEngineStop={() => {
              if (graphRef.current) {
                graphRef.current.zoomToFit(400); // Adjust the zoom level to fit all nodes
              }
            }}
          />
        </div>
      </div>

      <div style={styles.statusBox}>
        <span style={{ fontWeight: "bold" }}>Connection Status:</span>
        {connectionStatus}
      </div>

      <footer style={styles.footer}>
        <p style={styles.footerText}>You're somehow connected ❤️</p>
      </footer>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    width: "100vw",
    height: "100vh",
    background: "#000",
    color: "#fff",
    overflow: "hidden",
    fontFamily: "Iosevka, monospace",
  },
  header: {
    background: "#111",
    color: "#fff",
    padding: "10px 20px",
    borderBottom: "2px solid #fff",
    textAlign: "center",
  },
  headerTitle: {
    fontSize: "24px",
    margin: 0,
    textTransform: "uppercase",
  },
  mainContent: {
    display: "flex",
    height: "calc(100% - 120px)", // Adjust height to account for header and footer
  },
  sidebar: {
    width: "300px",
    background: "#111",
    padding: "20px",
    borderRight: "2px solid #fff",
    boxSizing: "border-box",
  },
  sidebarTitle: {
    fontSize: "20px",
    borderBottom: "1px solid #fff",
    paddingBottom: "10px",
    marginBottom: "10px",
    textTransform: "uppercase",
  },
  statusBox: {
    position: "absolute",
    top: "50px",
    left: "320px",
    background: "#111",
    padding: "8px 12px",
    borderRadius: "0",
    fontSize: "12px",
    fontWeight: "bold",
    border: "1px solid #fff",
  },
  closeButton: {
    marginTop: "10px",
    padding: "6px 10px",
    background: "#333",
    color: "#fff",
    border: "1px solid #fff",
    cursor: "pointer",
    width: "100%",
    textTransform: "uppercase",
    fontFamily: "Iosevka, monospace",
  },
  link: {
    color: "#fff",
    textDecoration: "none",
    fontWeight: "bold",
    display: "block",
    marginTop: "10px",
    borderBottom: "1px solid #fff",
    paddingBottom: "5px",
  },
  text: {
    fontSize: "14px",
    lineHeight: "1.4",
  },
  footer: {
    background: "#111",
    color: "#fff",
    padding: "10px 20px",
    borderTop: "2px solid #fff",
    textAlign: "center",
    fontSize: "12px",
  },
  footerText: {
    margin: 0,
  },
};

export default App;

