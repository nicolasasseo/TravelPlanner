import * as React from "react"

interface DialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  children: React.ReactNode
}

interface DialogContentProps {
  children: React.ReactNode
  className?: string
}

interface DialogHeaderProps {
  children: React.ReactNode
}

interface DialogFooterProps {
  children: React.ReactNode
}

interface DialogTitleProps {
  children: React.ReactNode
}

interface DialogDescriptionProps {
  children: React.ReactNode
}

const Dialog = ({ open, onOpenChange, children }: DialogProps) => {
  React.useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden"
    } else {
      document.body.style.overflow = "unset"
    }
    return () => {
      document.body.style.overflow = "unset"
    }
  }, [open])

  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      onClick={() => onOpenChange(false)}
    >
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm animate-in fade-in" />

      {/* Content */}
      <div onClick={(e) => e.stopPropagation()}>{children}</div>
    </div>
  )
}

const DialogContent = ({ children, className = "" }: DialogContentProps) => {
  return (
    <div
      className={`relative z-50 bg-white rounded-lg shadow-xl max-w-md w-full mx-4 animate-in zoom-in-95 ${className}`}
    >
      {children}
    </div>
  )
}

const DialogHeader = ({ children }: DialogHeaderProps) => {
  return <div className="px-6 pt-6 pb-4">{children}</div>
}

const DialogFooter = ({ children }: DialogFooterProps) => {
  return (
    <div className="px-6 pb-6 pt-4 flex gap-3 justify-end border-t border-gray-100">
      {children}
    </div>
  )
}

const DialogTitle = ({ children }: DialogTitleProps) => {
  return <h2 className="text-xl font-semibold text-gray-900">{children}</h2>
}

const DialogDescription = ({ children }: DialogDescriptionProps) => {
  return <p className="text-sm text-gray-500 mt-2">{children}</p>
}

export {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
}
