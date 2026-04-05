/** CSS Modules type declaration — tells TypeScript to accept .module.css imports */
declare module '*.module.css' {
  const classes: Record<string, string>
  export default classes
}
