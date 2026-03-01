# Auto Bone Connector

A Blender addon for streamlined bone rigging with intelligent connection tools, follow-through constraints, and collision support.

## Features

### Edit Mode Tools
- **Connect to Active** — Parent multiple bones to the active bone with flexible options:
  - *Keep Offset*: Parent while preserving current positions
  - *Connected*: Snap child heads to parent tail
  - *Tail to Head*: Move parent tail to child head
- **Chain Operations** — Connect selected bones in sequence (sorted by name)
- **Auto Connect by Distance** — Automatically parent bones to the nearest neighbor within a threshold
- **Disconnect Tools** — Disconnect bones or completely clear parenting

### Pose Mode Tools
- **Auto Damp Track Chain** — Add Damped Track constraints for automatic follow-through animation:
  - Gradient influence from root to tip
  - Two modes: track immediate child or track chain tip
  - Configurable influence values and track axis
- **Performance Controls** — Toggle constraints on/off to speed up viewport playback
- **Collision Constraints** — Add Limit Distance constraints for basic collision spheres
- **Spline IK Hair Setup** — Quick setup for hair/cable physics with curve-based Spline IK

## Installation

1. Download the latest release as a ZIP file
2. In Blender, go to **Edit > Preferences > Add-ons > Install...**
3. Select the downloaded ZIP file
4. Enable the addon by checking the checkbox

## Requirements

- Blender 3.0 or newer

## Usage

Access all tools in the 3D Viewport sidebar (**N** panel) under the **Bone Tools** tab.

### Edit Mode Workflow

1. Select multiple bones in Edit Mode
2. Choose your connection method from the panel:
   - Click **Keep Offset** to parent without moving
   - Click **Connected** to snap bones together
   - Use **Auto by Distance** to let the addon find nearest neighbors

### Pose Mode Workflow

#### Follow-Through Animation
1. Select all bones in a chain (in Pose Mode)
2. Adjust the settings:
   - **Mode**: Choose "Immediate Child" for chain hierarchy or "Chain Tip" for aiming at the end
   - **Root/Tip Influence**: Set how strongly each end follows (0 = rigid, 1 = full follow)
   - **Axis**: Which bone axis points toward the target
3. Click **Add Damp Track Chain**
4. Use **Toggle Damp Track** to temporarily disable for better playback performance

#### Collision Setup
1. Select the collision object as your **active** object
2. Add the bones you want constrained to the selection
3. Click **Add Collision Sphere** and configure the distance

#### Hair/Cable Physics
1. Select the curve object as your **active** object
2. Add the chain's root bone to the selection
3. Click **Setup Spline IK** and set chain length
4. Add Soft Body physics to the curve for dynamic simulation

## Tips

- **Performance**: Use "Disable All (Fast)" when animating complex rigs, then "Enable All (Normal)" for final review
- **Naming**: Bones are sorted alphabetically for chain operations — consistent naming helps predictable results
- **Influence Curves**: Set root influence low (0.1) and tip high (1.0) for natural follow-through on tails, hair, or cables

## License

[Your License Here] — e.g., MIT, GPL, etc.

## Author

**Garuh143**

---

Contributions and feedback welcome!
