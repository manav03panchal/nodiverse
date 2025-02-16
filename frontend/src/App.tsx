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
  const eventName = "HackED";
  const graphRef = useRef(null);

  // Logged-in user ID (replace with actual auth logic)
  const loggedInUserId = "80aace7b-fcee-44b6-a3c6-84bf8ca6a84a";

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
                ? "#ffcc00" // ✅ Only gold for the logged-in user
                : p.role === "organizer"
                  ? "#e63946" // ✅ Organizers in red
                  : "#457b9d", // ✅ Participants in blue
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

  const handleNodeClick = (node: any) => {
    if (node.role) {
      setSelectedUser(node);
    }
  };

  return (
    <div style={styles.container}>
      {/* Sidebar */}
      <div style={styles.sidebar}>
        <h2 style={styles.sidebarTitle}>
          {selectedUser ? selectedUser.name : "Select a User"}
        </h2>
        {selectedUser ? (
          <>
            <p>
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
          <p>Click on a user to view details.</p>
        )}
      </div>

      {/* Status Bar */}
      <div style={styles.statusBox}>
        <span style={{ fontWeight: "bold" }}>Connection Status:</span>{" "}
        {connectionStatus}
      </div>

      {/* Graph */}
      <ForceGraph2D
        ref={graphRef}
        graphData={graphData}
        nodeLabel={() => ""} // ✅ No names on nodes
        nodeColor={(node) => node.color}
        onNodeClick={handleNodeClick}
        onNodeHover={(node) => setHoveredNode(node || null)} // ✅ Show name only on hover
        width={window.innerWidth - 300}
        height={window.innerHeight}
        linkDirectionalArrowLength={4}
        linkDirectionalArrowRelPos={1}
        nodeCanvasObjectMode={(node) =>
          hoveredNode?.id === node.id ? "before" : undefined
        }
        nodeCanvasObject={(node, ctx, globalScale) => {
          if (hoveredNode?.id === node.id) {
            const label = node.name;
            const fontSize = 12 / globalScale;
            ctx.font = `${fontSize}px Arial`;
            ctx.textAlign = "center";
            ctx.textBaseline = "top"; // ✅ Name appears below the node
            ctx.fillStyle = "#fff";
            ctx.fillText(label, node.x!, node.y! + 10); // ✅ Shift text down by 10 pixels
          }
        }}
        d3ForceCollide={(node) => 10} // Radius of collision force
        d3ForceX={d3.forceX().strength(0.2)} // Increase X axis attraction
        d3ForceY={d3.forceY().strength(0.2)} // Increase Y axis attraction
        d3ForceCharge={-50} // Reduce repulsion
        linkDirectionalParticles={2}
        linkDirectionalParticleWidth={4}
        linkDistance={30} // Set desired link distance
        centerAt={{ x: 0.5, y: 0.5 }} // Center the graph
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

          minX -= 100;
          maxX += 100;
          minY -= 100;
          maxY += 100;

          ctx.strokeStyle = "#fff";
          ctx.lineWidth = 4;
          ctx.strokeRect(minX, minY, maxX - minX, maxY - minY);

          ctx.font = "16px Arial";
          ctx.fillStyle = "#fff";
          ctx.textAlign = "center";
          ctx.fillText(eventName, (minX + maxX) / 2, minY - 15);
        }}
      />
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: "flex",
    width: "100vw",
    height: "100vh",
    background: "#121212",
    color: "white",
    overflow: "hidden",
  },
  sidebar: {
    width: "300px",
    height: "100vh",
    background: "#222",
    padding: "20px",
    borderRight: "4px solid #fff",
  },
  sidebarTitle: {
    fontSize: "22px",
    borderBottom: "2px solid #fff",
    paddingBottom: "10px",
  },
  statusBox: {
    position: "absolute",
    top: 10,
    left: 320,
    background: "#333",
    padding: "8px 12px",
    borderRadius: "4px",
    fontSize: "14px",
    fontWeight: "bold",
    border: "1px solid white",
  },
  closeButton: {
    marginTop: "10px",
    padding: "6px 10px",
    background: "#e63946",
    color: "white",
    border: "none",
    cursor: "pointer",
    width: "100%",
  },
  link: {
    color: "#ffca3a",
    textDecoration: "none",
    fontWeight: "bold",
    display: "block",
    marginTop: "10px",
  },
};

export default App;

