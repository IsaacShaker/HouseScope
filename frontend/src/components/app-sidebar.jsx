import * as React from "react"
import {
  LayoutDashboardIcon,
  HomeIcon,
  CalculatorIcon,
  WalletIcon,
  ArrowLeftRightIcon,
  SettingsIcon,
  HelpCircleIcon,
} from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavSecondary } from "@/components/nav-secondary"
import { NavUser } from "@/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

const data = {
  user: {
    name: JSON.parse(localStorage.getItem('user') || '{}').email || "User",
    email: JSON.parse(localStorage.getItem('user') || '{}').email || "user@example.com",
    avatar: "",
  },
  navMain: [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: LayoutDashboardIcon,
    },
    {
      title: "Properties",
      url: "/properties",
      icon: HomeIcon,
    },
    {
      title: "Affordability",
      url: "/affordability",
      icon: CalculatorIcon,
    },
    {
      title: "Accounts",
      url: "/accounts",
      icon: WalletIcon,
    },
    {
      title: "Transactions",
      url: "/transactions",
      icon: ArrowLeftRightIcon,
    },
  ],
  navSecondary: [
    {
      title: "Settings",
      url: "#",
      icon: SettingsIcon,
    },
    {
      title: "Help",
      url: "#",
      icon: HelpCircleIcon,
    },
  ],
}

export function AppSidebar({
  ...props
}) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild className="data-[slot=sidebar-menu-button]:!p-1.5">
              <a href="/dashboard">
                <HomeIcon className="h-5 w-5" />
                <span className="text-base font-semibold">🏠 HouseScope</span>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
        <NavSecondary items={data.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
    </Sidebar>
  );
}
