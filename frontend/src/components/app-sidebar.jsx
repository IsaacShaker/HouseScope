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

const navMain = [
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
];

const navSecondary = [
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
];

export function AppSidebar({
  ...props
}) {
  const [user, setUser] = React.useState(() => {
    const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
    return {
      name: storedUser.full_name || storedUser.email || "User",
      email: storedUser.email || "user@example.com",
      avatar: "",
    };
  });

  // Update user data when localStorage changes
  React.useEffect(() => {
    const handleStorageChange = () => {
      const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
      setUser({
        name: storedUser.full_name || storedUser.email || "User",
        email: storedUser.email || "user@example.com",
        avatar: "",
      });
    };

    window.addEventListener('storage', handleStorageChange);
    
    // Also listen for custom event when user logs in
    window.addEventListener('userUpdated', handleStorageChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('userUpdated', handleStorageChange);
    };
  }, []);

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
        <NavMain items={navMain} />
        <NavSecondary items={navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={user} />
      </SidebarFooter>
    </Sidebar>
  );
}
